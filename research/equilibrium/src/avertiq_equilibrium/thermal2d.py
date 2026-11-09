"""Well-balanced 2D conservative thermal/phase/gravity research prototype.

Eight densities: five total components, horizontal/vertical momentum, and
internal + kinetic + gravitational-potential energy. No field-validation claim.
"""
import math
import numpy as np

from .properties import Properties, COMPONENTS, PROPANE, WATER
from .equilibrium import Equilibrium
from .equilibrium_uv import EquilibriumUV
from .study import build_source, ambient_stream
from .cases import provenance

COLUMNS = ["rho_"+s+"_kg_m3" for s in COMPONENTS]+[
    "momentum_x_kg_m2_s","momentum_z_kg_m2_s","energy_including_potential_J_m3"]


def _number(v,name,positive=False):
    if isinstance(v,(bool,str,bytes)):
        raise ValueError(name+" must be finite numeric")
    try:v=float(v)
    except (TypeError,ValueError,OverflowError) as exc:raise ValueError(name+" must be numeric") from exc
    if not math.isfinite(v) or v<0 or (positive and v==0):
        raise ValueError("Invalid "+name)
    return v


def initialize_thermal2d(properties=None, *, nx=4,nz=4,length_x_m=1.,height_m=1.,
                         gravity_m_s2=9.81,blob=True):
    """Return conservative cells and an exact-cell-average isothermal reference."""
    if any(isinstance(n,bool) or not isinstance(n,int) or not 4<=n<=16 for n in (nx,nz)):
        raise ValueError("nx/nz must be integers in [4,16]")
    lx=_number(length_x_m,"length",True);height=_number(height_m,"height",True)
    g=_number(gravity_m_s2,"gravity")
    p=properties or Properties(); eq=Equilibrium(p)
    ambient=ambient_stream(p)
    na=ambient.mol_per_kg;ha=ambient.enthalpy_J_kg
    if blob:
        source=build_source(p).state
        ns=source.component_amounts()/source.mass_kg;hs=source.enthalpy_J/source.mass_kg
    k=ambient.metadata["bulk_density_kg_m3"]/102500.
    dz=height/nz; z=(np.arange(nz)+.5)*dz
    pf=102500.*np.exp(-g*k*np.arange(nz+1)*dz)
    if g:
        rb=pf[:-1]*(-np.expm1(-g*k*dz))/(g*dz)
        pc=rb/k
    else:
        pc=np.full(nz,102500.);rb=k*pc
    reference=np.empty((nz,nx,8));q=np.empty_like(reference)
    x=(np.arange(nx)+.5)*lx/nx
    for j in range(nz):
        base=eq.tp(283.05,float(pc[j]),na)
        rhob=base.mass_kg/base.volume_m3
        eb=base.enthalpy_J/base.mass_kg-pc[j]/rhob
        reference[j,:,:5]=rhob*na*p.mw
        reference[j,:,5:7]=0.
        reference[j,:,7]=rhob*(eb+g*z[j])
        if not blob:
            q[j]=reference[j]
            continue
        for i in range(nx):
            f=(.1+.6*math.exp(-((x[i]/lx-.5)**2+(z[j]/height-.65)**2)/.08)) if blob else 0.
            n=f*ns+(1-f)*na;h=f*hs+(1-f)*ha
            state=eq.ph(float(pc[j]),n,h)
            rho=state.mass_kg/state.volume_m3
            q[j,i,:5]=rho*n*p.mw
            q[j,i,5:7]=0.
            q[j,i,7]=rho*(state.enthalpy_J/state.mass_kg-pc[j]/rho+g*z[j])
    ref={"conserved":reference,"pressure_faces_Pa":pf,"pressure_cells_Pa":pc,
         "density_cells_kg_m3":rb,
         "metadata":{"temperature_K":283.05,"bottom_pressure_Pa":102500.,
                     "density_per_pressure":k,"kind":"isothermal ideal-gas exact cell average",
                     "gravity_m_s2":g,"height_m":height}}
    return q,ref


def _riemann(left,right,pl,pr,cl,cr,normal):
    """General-EOS HLLC flux; transverse momentum scales with star density."""
    rho=left[:,:5].sum(1);rhor=right[:,:5].sum(1)
    u=left[:,normal]/rho;ur=right[:,normal]/rhor
    fl=left*u[:,None];fr=right*ur[:,None]
    fl[:,normal]+=pl;fr[:,normal]+=pr
    fl[:,7]+=pl*u;fr[:,7]+=pr*ur
    sl=np.minimum(u-cl,ur-cr);sr=np.maximum(u+cl,ur+cr)
    den=rho*(sl-u)-rhor*(sr-ur)
    if (den==0).any():raise RuntimeError("Degenerate HLLC contact")
    sm=(pr-pl+rho*u*(sl-u)-rhor*ur*(sr-ur))/den
    psl=pl+rho*(sl-u)*(sm-u);psr=pr+rhor*(sr-ur)*(sm-ur)
    if (not np.isfinite(sm).all() or (sm<=sl).any() or (sm>=sr).any()
            or (psl<=0).any() or (psr<=0).any()):
        raise RuntimeError("Inadmissible HLLC waves")
    def star(q,s,v,p,r,ps):
        factor=(s-v)/(s-sm)
        result=q*factor[:,None]
        result[:,normal]=r*factor*sm
        result[:,7]=((s-v)*q[:,7]-p*v+ps*sm)/(s-sm)
        if not np.isfinite(result).all() or (result[:,:5]<0).any():
            raise RuntimeError("Inadmissible HLLC star")
        return result
    ls=star(left,sl,u,pl,rho,psl);rs=star(right,sr,ur,pr,rhor,psr)
    flux=np.where((sl>=0)[:,None],fl,
          np.where((sm>=0)[:,None],fl+sl[:,None]*(ls-left),
          np.where((sr>0)[:,None],fr+sr[:,None]*(rs-right),fr)))
    return flux


def solve_thermal2d(conserved, *, properties=None,length_x_m=1.,height_m=1.,
                    gravity_m_s2=9.81,duration_s=3e-4,conductivity_W_m_K=10.,
                    cfl=.25,reference=None,atmosphere=None,max_timestep_s=None):
    """Conservative unsplit FV update with well-balanced reference flux correction."""
    q=np.asarray(conserved,dtype=float).copy()
    if q.ndim!=3 or q.shape[2]!=8 or min(q.shape[:2])<4 or max(q.shape[:2])>16:
        raise ValueError("Expected (nz,nx,8) with axes in [4,16]")
    if not np.isfinite(q).all() or (q[:,:,:5]<0).any() or (q[:,:,:5].sum(2)<=0).any():
        raise ValueError("Finite conservative cells and nonnegative species required")
    nz,nx=q.shape[:2]
    lx=_number(length_x_m,"length",True);height=_number(height_m,"height",True)
    g=_number(gravity_m_s2,"gravity");duration=_number(duration_s,"duration")
    conductivity=_number(conductivity_W_m_K,"conductivity")
    cfl=_number(cfl,"CFL",True)
    step_cap = math.inf if max_timestep_s is None else _number(max_timestep_s,"maximum timestep",True)
    if cfl>.4:raise ValueError("CFL must not exceed .4")
    props=properties or Properties();eos=EquilibriumUV(props)
    if atmosphere is not None:
        atmosphere.begin_run(nx, nz, lx, height, g)
        reference=atmosphere.reference
    if reference is None:
        _,reference=initialize_thermal2d(props,nx=nx,nz=nz,length_x_m=lx,height_m=height,gravity_m_s2=g,blob=False)
    bar=np.asarray(reference["conserved"],dtype=float)
    pf=np.asarray(reference["pressure_faces_Pa"],dtype=float)
    pc=np.asarray(reference["pressure_cells_Pa"],dtype=float)
    if bar.shape!=q.shape or pf.shape!=(nz+1,) or pc.shape!=(nz,):
        raise ValueError("Reference grid shape mismatch")
    if (reference["metadata"]["gravity_m_s2"]!=g or reference["metadata"]["height_m"]!=height
            or not np.isfinite(bar).all() or not np.isfinite(pf).all()):
        raise ValueError("Reference configuration mismatch")
    if atmosphere is None:
        _,expected=initialize_thermal2d(props,nx=nx,nz=nz,length_x_m=lx,height_m=height,gravity_m_s2=g,blob=False)
    else:
        expected=atmosphere.canonical_reference()
    if (not np.allclose(bar,expected["conserved"],rtol=5e-11,atol=1e-10)
            or not np.allclose(pf,expected["pressure_faces_Pa"],rtol=1e-12,atol=1e-9)
            or not np.allclose(pc,expected["pressure_cells_Pa"],rtol=1e-12,atol=1e-9)):
        raise ValueError("Reference must be the declared isothermal hydrostatic state")
    dx=lx/nx;dz=height/nz
    z=(np.arange(nz)+.5)*dz;phi=g*z[:,None]
    cache={}
    def decode(array,derivatives=False):
        data=[]
        for j in range(nz):
            line=[]
            for i in range(nx):
                row=array[j,i];rho=float(row[:5].sum())
                if not np.isfinite(row).all() or (row[:5]<0).any() or rho<=0:
                    raise ValueError("Non-admissible trial mass state")
                ux=float(row[5]/rho);uz=float(row[6]/rho)
                e=float(row[7]/rho-.5*(ux*ux+uz*uz)-g*z[j])
                n=row[:5]/(rho*props.mw)
                key=(rho,e,*n.tolist())
                if key not in cache:
                    s=eos.solve(rho,n,e)
                    cache[key]={"state":s,"rho":rho,"e":e,"n":n}
                base=cache[key]
                if derivatives:
                    if "c" not in base:base["c"]=eos.sound_speed(rho,n,e,state=base["state"])
                    if conductivity and "cv" not in base:
                        base["cv"]=eos.heat_capacity_cv(rho,n,e,state=base["state"])
                rec=dict(base);rec["u"]=ux;rec["w"]=uz
                line.append(rec)
            data.append(line)
        return data
    def fields(records):
        pressure=np.array([[r["state"].pressure_Pa for r in line] for line in records])
        sound=np.array([[r["c"] for r in line] for line in records])
        return pressure,sound
    def fluxes(array,records):
        if atmosphere is not None:
            return atmosphere.fluxes(array,records,_riemann)
        pressure,sound=fields(records)
        gas=array.copy();gas[:,:,7]-=array[:,:,:5].sum(2)*phi
        right=np.roll(gas,-1,axis=1)
        fx=_riemann(gas.reshape(-1,8),right.reshape(-1,8),pressure.ravel(),
                    np.roll(pressure,-1,axis=1).ravel(),sound.ravel(),
                    np.roll(sound,-1,axis=1).ravel(),5).reshape(nz,nx,8)
        fx[:,:,7]+=phi*fx[:,:,:5].sum(2)
        bottom=gas[0:1].copy();bottom[:,:,6]*=-1
        top=gas[-1:].copy();top[:,:,6]*=-1
        lower=np.concatenate([bottom,gas],axis=0)
        upper=np.concatenate([gas,top],axis=0)
        pl=np.concatenate([pressure[0:1],pressure],axis=0)
        pr=np.concatenate([pressure,pressure[-1:]],axis=0)
        cl=np.concatenate([sound[0:1],sound],axis=0)
        cr=np.concatenate([sound,sound[-1:]],axis=0)
        fz=_riemann(lower.reshape(-1,8),upper.reshape(-1,8),pl.ravel(),pr.ravel(),
                    cl.ravel(),cr.ravel(),6).reshape(nz+1,nx,8)
        fz[:,:,7]+=(g*np.arange(nz+1)*dz)[:,None]*fz[:,:,:5].sum(2)
        # Reflection symmetry sets zero mass, tangential momentum and energy flux
        # exactly; keep numerical wall pressure in the normal momentum flux.
        fz[[0,-1],:,:5]=0.;fz[[0,-1],:,5]=0.;fz[[0,-1],:,7]=0.
        return fx,fz
    bar_records=decode(bar,True)
    fxbar,fzbar=fluxes(bar,bar_records)
    physical_x=np.zeros_like(fxbar);physical_x[:,:,5]=pc[:,None]
    physical_z=np.zeros_like(fzbar);physical_z[:,:,6]=pf[:,None]
    if atmosphere is not None:
        physical_x,physical_z=atmosphere.physical_reference_fluxes()
    original=q.copy();initial=q.sum((0,1))*dx*dz
    boundary=np.zeros(8);gravity_impulse=0.
    elapsed=0.;steps=0;retries=0;max_courant=0.;max_fourier=0.
    while elapsed<duration:
        records=decode(q,True)
        u=np.array([[r["u"] for r in line] for line in records])
        w=np.array([[r["w"] for r in line] for line in records])
        sound=np.array([[r["c"] for r in line] for line in records])
        rho=q[:,:,:5].sum(2)
        rate=np.max((np.abs(u)+sound)/dx+(np.abs(w)+sound)/dz)
        dt=min(duration-elapsed,cfl/float(rate),step_cap)
        cv=np.array([[r.get("cv",math.inf) for r in line] for line in records])
        if conductivity:
            dt=min(dt,.15*float(np.min(rho*cv))/(conductivity*(1/dx**2+1/dz**2)))
        if not math.isfinite(dt) or dt<=0:raise RuntimeError("Invalid coupled timestep")
        fx,fz=fluxes(q,records)
        fx=fx-fxbar+physical_x;fz=fz-fzbar+physical_z
        if conductivity:
            t=np.array([[r["state"].temperature_K for r in line] for line in records])
            if atmosphere is None:
                fx[:,:,7]-=conductivity*(np.roll(t,-1,axis=1)-t)/dx
            else:
                fx[:,1:-1,7]-=conductivity*(t[:,1:]-t[:,:-1])/dx
            fz[1:-1,:,7]-=conductivity*(t[1:]-t[:-1])/dz
        if atmosphere is not None:
            atmosphere.apply_source(fx)
            rhs=-(fx[:,1:]-fx[:,:-1])/dx-(fz[1:]-fz[:-1])/dz
        else:
            rhs=-(fx-np.roll(fx,1,axis=1))/dx-(fz[1:]-fz[:-1])/dz
        rhs[:,:,6]-=rho*g
        for attempt in range(13):
            candidate=q+dt*rhs
            try:decode(candidate);break
            except (ValueError,RuntimeError):
                dt*=.5;retries+=1
                if attempt==12:raise RuntimeError("No admissible 2D thermal timestep")
        q=candidate
        boundary+=dt*dx*np.sum(fz[0]-fz[-1],axis=0)
        if atmosphere is not None:
            boundary+=dt*dz*np.sum(fx[:,0]-fx[:,-1],axis=0)
            atmosphere.record_fluxes(fx,fz,dt)
        gravity_impulse-=dt*g*float(rho.sum())*dx*dz
        elapsed+=dt;steps+=1
        if duration-elapsed<=8*np.finfo(float).eps*max(duration,1e-30):elapsed=duration
        max_courant=max(max_courant,float(rate)*dt)
        if conductivity:
            max_fourier=max(max_fourier,float(np.max(conductivity*dt/(rho*cv)))*(1/dx**2+1/dz**2))
        if steps>1000:raise RuntimeError("Coupled run exceeds 1000 steps")
    final=q.sum((0,1))*dx*dz
    source=np.zeros(8);source[6]=gravity_impulse
    residual=final-initial-boundary-source
    scale=np.maximum(np.sum(np.abs(original),(0,1))*dx*dz,1.)
    if not np.isfinite(q).all() or np.max(np.abs(residual)/scale)>1e-8:
        raise RuntimeError("2D conservative boundary/source budget failed")
    records=decode(q)
    cells=[]
    for j in range(nz):
        for i in range(nx):
            rec=records[j][i];s=rec["state"]
            phases={"gas":float(s.gas_mol@props.mw)/s.mass_kg,
                    "propane_liquid":s.propane_liquid_mol*props.mw[PROPANE]/s.mass_kg,
                    "water_liquid":s.water_liquid_mol*props.mw[WATER]/s.mass_kg,
                    "water_ice":s.ice_mol*props.mw[WATER]/s.mass_kg}
            cells.append({"x_m":(i+.5)*dx,"z_m":z[j],"density_kg_m3":rec["rho"],
                          "velocity_x_m_s":rec["u"],"velocity_z_m_s":rec["w"],
                          "u_m_s":rec["u"],"w_m_s":rec["w"],
                          "internal_energy_J_kg":rec["e"],
                          "component_mol_per_kg":dict(zip(COMPONENTS,rec["n"].tolist())),
                          "temperature_K":s.temperature_K,"pressure_Pa":s.pressure_Pa,
                          "phase_mass_fractions":{k:float(v) for k,v in phases.items()},
                          "volume_constraint_relative_residual":float(s.volume_m3*rec["rho"]-1.)})
    result={"schema_version":1,"model":"2D conservative well-balanced Euler-HLLC/Fourier/gravity with equilibrium UV EOS",
            "field_prediction_ready":False,"column_names":COLUMNS,
            "initial_conserved":original.tolist(),"final_conserved":q.tolist(),"cells":cells,
            "reference":{"conserved":bar.tolist(),"pressure_faces_Pa":pf.tolist(),
                         "pressure_cells_Pa":pc.tolist(),"metadata":reference["metadata"]},
            "configuration":{"nx":nx,"nz":nz,"length_x_m":lx,"height_m":height,
                             "duration_s":duration,"gravity_m_s2":g,"conductivity_W_m_K":conductivity,
                             "cfl":cfl,"boundary":("periodic x; reflecting adiabatic z" if atmosphere is None else "ambient inflow; extrapolating right/top outflow with reservoir backflow; reflecting adiabatic ground")},
            "diagnostics":{"steps":steps,"elapsed_s":elapsed,"timestep_retries":retries,
                           "maximum_acoustic_courant":max_courant,"maximum_thermal_fourier":max_fourier,
                           "initial_integrals":initial.tolist(),"final_integrals":final.tolist(),
                           "accumulated_boundary_integrals":boundary.tolist(),
                           "accumulated_gravity_momentum_z":gravity_impulse,
                           "budget_residuals":residual.tolist(),
                           "maximum_relative_budget_residual":float(np.max(np.abs(residual)/scale))},
            "limitations":["Synthetic tiny closed-box compressible equilibrium research, not EEC550 field validation.",
                           "Fixed isothermal reference well balancing; no universal hydrostatic equilibrium preservation.",
                           "Common equilibrium velocity/temperature; no slip, phase rates, viscosity or turbulence.",
                           "Synthetic prescribed conductivity; no ground heat, release inlet, open boundary or terrain.",
                           "First-order reference-corrected HLLC; strong shocks and arbitrary moving contacts unvalidated."],
            "provenance":provenance()}
    if atmosphere is not None:
        result["atmospheric"]=atmosphere.summary()
        result["limitations"]=[x for x in result["limitations"] if "closed-box" not in x and "release inlet" not in x]
        result["limitations"].extend(atmosphere.limitations)
    return result


def run_thermal2d(properties=None,**options):
    props=properties or Properties()
    nx=options.pop("nx",4);nz=options.pop("nz",4);blob=options.pop("blob",True)
    initial,reference=initialize_thermal2d(props,nx=nx,nz=nz,
        length_x_m=options.get("length_x_m",1.),height_m=options.get("height_m",1.),
        gravity_m_s2=options.get("gravity_m_s2",9.81),blob=blob)
    result=solve_thermal2d(initial,properties=props,reference=reference,**options)
    result["initial_condition"]="Synthetic H00/ambient mass-fraction blob" if blob else "Isothermal hydrostatic reference"
    return result
