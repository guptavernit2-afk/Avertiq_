"""2D frozen-endpoint variable-density incompressible flow research.

Conservative volume-fraction transport; staggered variable-coefficient projection.
Velocity-form momentum is donor-cell discretized, not a conservative rho*u scheme.
No evolving equilibrium energy/phase closure or atmospheric field validation.
"""
import math
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

from .cases import provenance


def _positive(value, name, zero=False):
    if isinstance(value, (bool, str, bytes)):
        raise ValueError(f"{name} must be numeric")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(value) or value < 0 or (value == 0 and not zero):
        raise ValueError(f"{name} must be finite and {'nonnegative' if zero else 'positive'}")
    return value


def _fields(u, w, rho):
    rho = np.asarray(rho, dtype=float)
    u, w = np.asarray(u, dtype=float), np.asarray(w, dtype=float)
    if rho.ndim != 2 or min(rho.shape) < 4 or rho.size > 16384:
        raise ValueError("Density needs a 2D grid, at least 4 cells per axis and at most 16384 cells")
    nz, nx = rho.shape
    if u.shape != rho.shape or w.shape != (nz+1, nx):
        raise ValueError("MAC field shapes do not match density")
    if not all(np.isfinite(a).all() for a in (u, w, rho)) or (rho <= 0).any():
        raise ValueError("Fields must be finite with positive density")
    if np.max(np.abs(w[[0,-1]])) > 1e-12:
        raise ValueError("Impermeable wall-normal velocities must be zero")
    return u.copy(), w.copy(), rho.copy()


def divergence(u, w, dx, dz):
    return (np.roll(u,-1,axis=1)-u)/dx+(w[1:]-w[:-1])/dz


def project_velocity(u, w, rho, dx, dz, dt):
    """Return corrected MAC velocities, reduced pressure and projection audit.

    u[j,i] is left x-face; w[j,i] is lower z-face. x is periodic; z walls
    impermeable. p[0,0]=0 fixes the pressure gauge, not physical pressure.
    """
    dx, dz, dt = (_positive(v,n) for v,n in ((dx,"dx"),(dz,"dz"),(dt,"dt")))
    u, w, rho = _fields(u,w,rho)
    nz,nx=rho.shape
    bx=2/(rho+np.roll(rho,1,axis=1))
    bz=2/(rho[1:]+rho[:-1])
    rows=[];cols=[];values=[]
    def edge(a,b,weight):
        rows.extend((a,a,b,b));cols.extend((a,b,a,b));values.extend((weight,-weight,-weight,weight))
    for j in range(nz):
        for i in range(nx):
            edge(j*nx+i,j*nx+(i+1)%nx,bx[j,(i+1)%nx]/dx**2)
    for j in range(nz-1):
        for i in range(nx):
            edge(j*nx+i,(j+1)*nx+i,bz[j,i]/dz**2)
    matrix=coo_matrix((values,(rows,cols)),shape=(rho.size,rho.size)).tocsr()
    rhs=-divergence(u,w,dx,dz).ravel()/dt
    compatibility=float(abs(rhs.sum())/max(1.,np.abs(rhs).sum()))
    if compatibility>1e-10:
        raise RuntimeError("Pressure Neumann compatibility failed")
    p=np.zeros(rho.size)
    p[1:]=spsolve(matrix[1:,1:],rhs[1:])
    residual=matrix@p-rhs
    relative=float(np.max(np.abs(residual))/max(1.,np.max(np.abs(rhs))))
    p=p.reshape(rho.shape)
    u-=dt*bx*(p-np.roll(p,1,axis=1))/dx
    w[1:-1]-=dt*bz*(p[1:]-p[:-1])/dz
    w[[0,-1]]=0.
    div=float(np.max(np.abs(divergence(u,w,dx,dz))))
    if not all(np.isfinite(a).all() for a in (u,w,p)) or not math.isfinite(relative) or not math.isfinite(div) or relative>1e-8 or div>1e-8:
        raise RuntimeError("Pressure projection residual/divergence gate failed")
    return u,w,p,{"relative_pressure_residual":relative,
                  "max_divergence_s_inv":div,
                  "neumann_compatibility_residual":compatibility}


def advect_fraction(alpha,u,w,dx,dz,dt):
    """Conservative shared-face upwind flux, no clipping."""
    alpha=np.asarray(alpha,dtype=float)
    u,w,_=_fields(u,w,np.ones_like(alpha))
    if not np.isfinite(alpha).all() or alpha.min()<-1e-12 or alpha.max()>1+1e-12:
        raise ValueError("Volume fraction must be finite and bounded")
    dx,dz,dt=(_positive(v,n) for v,n in ((dx,"dx"),(dz,"dz"),(dt,"dt")))
    outgoing=(np.maximum(np.roll(u,-1,axis=1),0)+np.maximum(-u,0))/dx
    outgoing+=(np.maximum(w[1:],0)+np.maximum(-w[:-1],0))/dz
    if dt*float(outgoing.max())>1+1e-12:
        raise ValueError("Volume-fraction CFL exceeds positivity limit")
    if np.max(np.abs(divergence(u,w,dx,dz)))>1e-8:
        raise ValueError("Fraction transport requires projected divergence-free velocity")
    fx=u*np.where(u>=0,np.roll(alpha,1,axis=1),alpha)
    fz=np.zeros_like(w)
    fz[1:-1]=w[1:-1]*np.where(w[1:-1]>=0,alpha[:-1],alpha[1:])
    result=alpha-dt*((np.roll(fx,-1,axis=1)-fx)/dx+(fz[1:]-fz[:-1])/dz)
    if not np.isfinite(result).all() or result.min()<-1e-10 or result.max()>1+1e-10:
        raise RuntimeError("Unclipped fraction bounds failed")
    return result


def _upwind_x(a,speed,dx):
    return np.where(speed>=0,(a-np.roll(a,1,axis=1))/dx,
                    (np.roll(a,-1,axis=1)-a)/dx)


def _predict(u,w,rho,dx,dz,dt,g,ref,nu):
    """Explicit velocity-form donor-cell convection, viscosity and buoyancy."""
    pad=np.pad(u,((1,1),(0,0)),mode="edge")
    watu=.25*(w[:-1]+w[1:]+np.roll(w[:-1],1,axis=1)+np.roll(w[1:],1,axis=1))
    duz=np.where(watu>=0,(u-pad[:-2])/dz,(pad[2:]-u)/dz)
    lapu=(np.roll(u,1,axis=1)-2*u+np.roll(u,-1,axis=1))/dx**2
    lapu+=(pad[:-2]-2*u+pad[2:])/dz**2
    up=u+dt*(-u*_upwind_x(u,u,dx)-watu*duz+nu*lapu)
    wi=w[1:-1]
    uc=.5*(u+np.roll(u,-1,axis=1))
    uatw=.5*(uc[:-1]+uc[1:])
    dwz=np.where(wi>=0,(wi-w[:-2])/dz,(w[2:]-wi)/dz)
    lapw=(np.roll(wi,1,axis=1)-2*wi+np.roll(wi,-1,axis=1))/dx**2
    lapw+=(w[:-2]-2*wi+w[2:])/dz**2
    rf=.5*(rho[:-1]+rho[1:])
    wp=np.zeros_like(w)
    wp[1:-1]=wi+dt*(-uatw*_upwind_x(wi,uatw,dx)-wi*dwz+nu*lapw-g*(rf-ref)/rf)
    return up,wp


def simulate_flow(alpha,*,rho_light=1.,rho_heavy=2.,length_x_m=10.,
                  height_m=10.,duration_s=.25,gravity_m_s2=9.81,
                  viscosity_m2_s=.01,initial_u=None,initial_w=None):
    """Frozen-endpoint, divergence-free mixture hydrodynamics on a closed layer."""
    a=np.asarray(alpha,dtype=float)
    light=_positive(rho_light,"light density");heavy=_positive(rho_heavy,"heavy density")
    if heavy<light:
        raise ValueError("Heavy endpoint density must be at least light density")
    lx=_positive(length_x_m,"length");height=_positive(height_m,"height")
    duration=_positive(duration_s,"duration",zero=True)
    g=_positive(gravity_m_s2,"gravity",zero=True);nu=_positive(viscosity_m2_s,"viscosity",zero=True)
    if a.ndim!=2 or not np.isfinite(a).all() or a.min()<0 or a.max()>1:
        raise ValueError("Initial volume fraction must be finite in [0,1]")
    nz,nx=a.shape
    u=np.zeros_like(a) if initial_u is None else np.asarray(initial_u,dtype=float)
    w=np.zeros((nz+1,nx)) if initial_w is None else np.asarray(initial_w,dtype=float)
    u,w,rho=_fields(u,w,light+(heavy-light)*a)
    dx,dz=lx/nx,height/nz
    u,w,p,projection=project_velocity(u,w,rho,dx,dz,1.)
    original=a.copy();z=(np.arange(nz)+.5)*dz
    def centroid(f):
        return float((f*z[:,None]).sum()/f.sum()) if f.sum()>0 else None
    initial_centroid=centroid(a);initial_mass=float(rho.sum()*dx*dz)
    elapsed=0.;steps=0;max_div=projection["max_divergence_s_inv"];max_pressure=projection["relative_pressure_residual"]
    while elapsed<duration:
        rate=float(np.max(np.abs(u))/dx+np.max(np.abs(w))/dz+2*nu*(1/dx**2+1/dz**2))
        # Bound acceleration-driven Courant growth as well as current flow.
        acceleration=g*max(abs(heavy-light)/light,1e-30)
        dt=min(duration-elapsed,.01,.35/max(rate,1e-30),
               math.sqrt(.1*min(dx,dz)/max(acceleration,1e-30)))
        up,wp=_predict(u,w,rho,dx,dz,dt,g,light,nu)
        u,w,p,audit=project_velocity(up,wp,rho,dx,dz,dt)
        a=advect_fraction(a,u,w,dx,dz,dt)
        rho=light+(heavy-light)*a
        max_div=max(max_div,audit["max_divergence_s_inv"])
        max_pressure=max(max_pressure,audit["relative_pressure_residual"])
        elapsed+=dt;steps+=1
        if duration-elapsed <= 8*np.finfo(float).eps*max(duration,1e-30):
            elapsed=duration
        if steps>10000:raise RuntimeError("Flow exceeds 10000 steps")
    final_mass=float(rho.sum()*dx*dz)
    relative_mass=abs(final_mass-initial_mass)/initial_mass
    if relative_mass>1e-10 or not all(np.isfinite(v).all() for v in (u,w,rho)):
        raise RuntimeError("Flow mass/finite-state gate failed")
    return {
        "schema_version":1,"model":"2D variable-density incompressible frozen-endpoint mixture",
        "field_prediction_ready":False,"initial_fraction":original.tolist(),"final_fraction":a.tolist(),
        "density_kg_m3":rho.tolist(),"u_face_m_s":u.tolist(),"w_face_m_s":w.tolist(),
        "pressure_Pa":p.tolist(),
        "configuration":{"nx":nx,"nz":nz,"length_x_m":lx,"height_m":height,"duration_s":duration,
                         "rho_light_kg_m3":light,"rho_heavy_kg_m3":heavy,"gravity_m_s2":g,
                         "kinematic_viscosity_m2_s":nu,"boundary":"periodic x; impermeable free-slip z"},
        "diagnostics":{"steps":steps,"elapsed_s":elapsed,"relative_mass_residual":relative_mass,
                       "initial_mass_kg_per_m_depth":initial_mass,"final_mass_kg_per_m_depth":final_mass,
                       "fraction_sum_residual":float(a.sum()-original.sum()),
                       "max_divergence_s_inv":max_div,"maximum_relative_pressure_residual":max_pressure,
                       "minimum_fraction":float(a.min()),"maximum_fraction":float(a.max()),
                       "initial_dense_centroid_z_m":initial_centroid,"final_dense_centroid_z_m":centroid(a)},
        "limitations":["Frozen endpoint volume-additive EOS; no evolving PH temperature/phase closure.",
                       "Velocity-form momentum advection is not discrete conservative rho*u transport.",
                       "Prescribed constant kinematic viscosity; no turbulence or atmosphere model.",
                       "2D closed-wall periodic-box research; not an EEC550 or terrain prediction.",
                       "Pressure is reduced pressure with arbitrary gauge, not absolute thermodynamic pressure."],
    }


def run_flow(properties=None,*,nx=24,nz=24,duration_s=.25,gravity_m_s2=9.81):
    from .properties import Properties
    from .study import build_source,ambient_stream
    if any(isinstance(v,bool) or not isinstance(v,int) or not 8<=v<=64 for v in (nx,nz)):
        raise ValueError("nx/nz must be integers from 8 to 64")
    props=properties or Properties()
    source=build_source(props,"H00");ambient=ambient_stream(props)
    dense=source.state.mass_kg/source.state.volume_m3
    light=ambient.metadata["bulk_density_kg_m3"]
    x=(np.arange(nx)+.5)*10/nx;z=(np.arange(nz)+.5)*10/nz
    alpha=.8*np.exp(-((x[None,:]-5)**2+(z[:,None]-6.5)**2)/(2*.8**2))
    result=simulate_flow(alpha,rho_light=light,rho_heavy=dense,duration_s=duration_s,gravity_m_s2=gravity_m_s2)
    result["source_endpoint"]=source.metadata
    result["ambient_endpoint"]=ambient.metadata
    result["initial_condition"]="Synthetic Gaussian dense-volume-fraction blob; not an experimental inlet"
    result["provenance"]=provenance()
    return result
