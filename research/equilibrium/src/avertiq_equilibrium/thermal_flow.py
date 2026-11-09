"""Conservative 1D Euler/heat transport with equilibrium UV thermodynamics.

Periodic, first-order HLLC (or Rusanov baseline) research solver. Conserved energy is internal plus
kinetic energy, not enthalpy. No gravity, turbulence or EEC550 field claim.
"""
import math
import numpy as np

from .cases import provenance
from .equilibrium import Equilibrium
from .properties import COMPONENTS, PROPANE, WATER, Properties
from .study import build_source, ambient_stream

COLUMN_NAMES = tuple("rho_"+name+"_kg_m3" for name in COMPONENTS)+(
    "momentum_kg_m2_s", "total_energy_J_m3")


def _number(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, (bool, str, bytes)):
        raise ValueError(f"{name} must be a finite number")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(value) or (positive and value <= 0) or (nonnegative and value < 0):
        raise ValueError(f"Invalid {name}")
    return value


def initialize_profile(properties=None, *, cells=8, length_m=1., velocity_m_s=0.):
    """Smooth synthetic fixed-pressure H00/ambient mass-fraction profile."""
    if isinstance(cells, bool) or not isinstance(cells, int) or not 4 <= cells <= 64:
        raise ValueError("cells must be an integer in [4,64]")
    _number(length_m, "length", positive=True)
    velocity = _number(velocity_m_s, "velocity")
    p = properties or Properties()
    source = build_source(p)
    ambient = ambient_stream(p)
    ns = source.state.component_amounts()/source.state.mass_kg
    hs = source.state.enthalpy_J/source.state.mass_kg
    fractions = .45+.35*np.cos(2*np.pi*(np.arange(cells)+.5)/cells)
    q = []
    for f in fractions:
        n = f*ns+(1-f)*ambient.mol_per_kg
        h = f*hs+(1-f)*ambient.enthalpy_J_kg
        state = Equilibrium(p).ph(102500., n, h)
        rho = state.mass_kg/state.volume_m3
        e = state.enthalpy_J/state.mass_kg-102500./rho
        q.append(np.r_[rho*n*p.mw, rho*velocity, rho*(e+.5*velocity**2)])
    return np.asarray(q)


# Retained as a convenience for independent callers; initialization is smooth,
# not a sharp contact. Rusanov still has mixture-interface pressure errors.
initialize_contact = initialize_profile


def conservative_flux(conserved, velocity, pressure):
    """Euler physical flux: species, rho*u^2+p, and (rho*E+p)*u."""
    q = np.asarray(conserved, dtype=float)
    u = np.asarray(velocity, dtype=float)
    pressure = np.asarray(pressure, dtype=float)
    result = q*u[:,None]
    result[:,5] += pressure
    result[:,6] += pressure*u
    return result



def interface_flux(conserved, velocity, pressure, sound_speed, *, scheme="hllc"):
    """Shared Euler interface flux; HLLC preserves stationary material contacts.

    General-EOS density/composition/energy enter the Rankine-Hugoniot star
    construction. Wave bounds use the numerical equilibrium sound speed.
    Candidate cells are separately checked by the UV closure; no star clipping.
    """
    q = np.asarray(conserved, dtype=float)
    u = np.asarray(velocity, dtype=float)
    p = np.asarray(pressure, dtype=float)
    c = np.asarray(sound_speed, dtype=float)
    if (q.ndim != 2 or q.shape[1] != 7 or u.shape != (len(q),)
            or p.shape != u.shape or c.shape != u.shape
            or not all(np.isfinite(a).all() for a in (q,u,p,c))
            or (q[:,:5] < 0).any() or (q[:,:5].sum(axis=1) <= 0).any()
            or (p <= 0).any() or (c <= 0).any()):
        raise ValueError("Invalid Euler interface states")
    physical = conservative_flux(q,u,p)
    right = np.roll(q,-1,axis=0)
    ur,pr,cr = np.roll(u,-1),np.roll(p,-1),np.roll(c,-1)
    physical_right = np.roll(physical,-1,axis=0)
    if scheme == "rusanov":
        speed = np.maximum(np.abs(u)+c,np.abs(ur)+cr)
        return .5*(physical+physical_right)-.5*speed[:,None]*(right-q)
    if scheme != "hllc":
        raise ValueError("Flux scheme must be hllc or rusanov")
    rho = q[:,:5].sum(axis=1)
    rhor = right[:,:5].sum(axis=1)
    sl = np.minimum(u-c,ur-cr)
    sr = np.maximum(u+c,ur+cr)
    denominator = rho*(sl-u)-rhor*(sr-ur)
    if np.any(denominator == 0):
        raise RuntimeError("Degenerate HLLC contact denominator")
    contact = (pr-p+rho*u*(sl-u)-rhor*ur*(sr-ur))/denominator
    pstar_l = p+rho*(sl-u)*(contact-u)
    pstar_r = pr+rhor*(sr-ur)*(contact-ur)
    if (not np.isfinite(contact).all() or (pstar_l <= 0).any()
            or (pstar_r <= 0).any() or (contact <= sl).any()
            or (contact >= sr).any()):
        raise RuntimeError("Inadmissible HLLC wave/star pressure")
    def star(state, speed, velocity, pressure, density, pstar):
        result = state*((speed-velocity)/(speed-contact))[:,None]
        rho_star = density*(speed-velocity)/(speed-contact)
        result[:,5] = rho_star*contact
        result[:,6] = ((speed-velocity)*state[:,6]-pressure*velocity
                       +pstar*contact)/(speed-contact)
        if (not np.isfinite(result).all() or (result[:,:5]<0).any()
                or (rho_star <= 0).any()):
            raise RuntimeError("Inadmissible conservative HLLC star state")
        return result
    left_star = star(q,sl,u,p,rho,pstar_l)
    right_star = star(right,sr,ur,pr,rhor,pstar_r)
    flux = np.empty_like(q)
    for index in range(len(q)):
        if sl[index] >= 0:
            flux[index] = physical[index]
        elif contact[index] >= 0:
            flux[index] = physical[index]+sl[index]*(left_star[index]-q[index])
        elif sr[index] > 0:
            flux[index] = physical_right[index]+sr[index]*(right_star[index]-right[index])
        else:
            flux[index] = physical_right[index]
    return flux


def solve_thermal_flow(conserved, *, properties=None, length_m=1.,
                       duration_s=3e-4, conductivity_W_m_K=10., cfl=.3, flux_scheme="hllc"):
    """Advance periodic conserved cells with local equilibrium pressure/phase.

    Fourier heat flux contributes only to total-energy interface flux. EOS
    positivity/domain failures trigger timestep reduction, never state clipping.
    """
    from .equilibrium_uv import EquilibriumUV
    q = np.asarray(conserved, dtype=float).copy()
    if q.ndim != 2 or q.shape[1] != 7 or not 4 <= len(q) <= 64:
        raise ValueError("Conserved array must have shape (4..64,7)")
    if not np.isfinite(q).all() or (q[:,:5] < 0).any() or (q[:,:5].sum(axis=1) <= 0).any():
        raise ValueError("Finite states and nonnegative species with positive mass required")
    length = _number(length_m, "length", positive=True)
    duration = _number(duration_s, "duration", nonnegative=True)
    conductivity = _number(conductivity_W_m_K, "conductivity", nonnegative=True)
    cfl = _number(cfl, "CFL", positive=True)
    if cfl > .5:
        raise ValueError("CFL must not exceed 0.5")
    if flux_scheme not in ("hllc", "rusanov"):
        raise ValueError("Flux scheme must be hllc or rusanov")
    p = properties or Properties()
    eos = EquilibriumUV(p)
    initial = q.copy()
    dx = length/len(q)
    cache = {}

    def decode(array, derivatives=False):
        records = []
        for row in array:
            rho = float(row[:5].sum())
            if not math.isfinite(rho) or rho <= 0 or (row[:5] < 0).any():
                raise ValueError("Nonpositive mass or negative component in trial state")
            u = float(row[5]/rho)
            e = float(row[6]/rho-.5*u*u)
            n = row[:5]/(rho*p.mw)
            key = (rho,e,*n.tolist())
            if key not in cache:
                state = eos.solve(rho,n,e)
                cache[key] = {"state":state, "rho":rho,"u":u,"e":e,"n":n}
            base = cache[key]
            state = base["state"]
            data = dict(base)
            data["u"] = u
            if derivatives:
                if "c" not in base:
                    base["c"] = eos.sound_speed(rho,n,e,state=state)
                data["c"] = base["c"]
                if conductivity:
                    if "cv" not in base:
                        base["cv"] = eos.heat_capacity_cv(rho,n,e,state=state)
                    data["cv"] = base["cv"]
            records.append(data)
        return records

    records = decode(q)
    elapsed = 0.
    steps = 0
    retries = 0
    maximum_courant = 0.
    maximum_fourier = 0.
    while elapsed < duration:
        records = decode(q, derivatives=True)
        waves = np.array([abs(v["u"])+v["c"] for v in records])
        dt = min(duration-elapsed, cfl*dx/float(waves.max()))
        cv = np.array([v.get("cv",math.inf) for v in records])
        rho = np.array([v["rho"] for v in records])
        if conductivity:
            finite_capacity = rho*cv
            dt = min(dt, .2*dx*dx*float(finite_capacity.min())/conductivity)
        if not math.isfinite(dt) or dt <= 0:
            raise RuntimeError("Thermal-flow timestep is not positive/finite")
        velocity = np.array([v["u"] for v in records])
        pressure = np.array([v["state"].pressure_Pa for v in records])
        temperatures = np.array([v["state"].temperature_K for v in records])
        sounds = np.array([v["c"] for v in records])
        flux = interface_flux(q,velocity,pressure,sounds,scheme=flux_scheme)
        flux[:,6] -= conductivity*(np.roll(temperatures,-1)-temperatures)/dx
        for attempt in range(13):
            candidate = q-dt/dx*(flux-np.roll(flux,1,axis=0))
            try:
                if not np.isfinite(candidate).all():
                    raise ValueError("Nonfinite trial state")
                decode(candidate)
                break
            except (ValueError, RuntimeError):
                dt *= .5
                retries += 1
                if attempt == 12:
                    raise RuntimeError("Unable to obtain admissible thermal-flow timestep")
        q = candidate
        elapsed += dt
        if duration-elapsed <= 8*np.finfo(float).eps*max(duration,1e-30):
            elapsed = duration
        maximum_courant = max(maximum_courant,float(waves.max())*dt/dx)
        if conductivity:
            maximum_fourier = max(maximum_fourier,float(np.max(conductivity*dt/(rho*cv*dx*dx))))
        steps += 1
        if steps > 1000:
            raise RuntimeError("Thermal flow exceeds 1000 steps")
    records = decode(q)
    initial_integrals = initial.sum(axis=0)*dx
    final_integrals = q.sum(axis=0)*dx
    residual = final_integrals-initial_integrals
    relative = np.abs(residual)/np.maximum(np.sum(np.abs(initial),axis=0)*dx,1.)
    if not np.isfinite(q).all() or np.max(relative)>1e-9:
        raise RuntimeError("Periodic species/momentum/total-energy conservation failed")
    cells = []
    for index,rec in enumerate(records):
        s = rec["state"]
        phases = {"gas":float(s.gas_mol@p.mw)/s.mass_kg,
                  "propane_liquid":s.propane_liquid_mol*p.mw[PROPANE]/s.mass_kg,
                  "water_liquid":s.water_liquid_mol*p.mw[WATER]/s.mass_kg,
                  "water_ice":s.ice_mol*p.mw[WATER]/s.mass_kg}
        cells.append({"x_m":(index+.5)*dx, "density_kg_m3":rec["rho"],
                      "velocity_m_s":rec["u"],"internal_energy_J_kg":rec["e"],
                      "component_mol_per_kg":dict(zip(COMPONENTS,rec["n"].tolist())),
                      "temperature_K":s.temperature_K,"pressure_Pa":s.pressure_Pa,
                      "phase_mass_fractions":{k:float(v) for k,v in phases.items()},
                      "volume_constraint_relative_residual":float(s.volume_m3*rec["rho"]-1.)})
    return {
        "schema_version":1, "model":"1D conservative Euler/"+flux_scheme+"/Fourier with equilibrium UV EOS",
        "field_prediction_ready":False,
        "column_names":list(COLUMN_NAMES),
        "initial_conserved":initial.tolist(),"final_conserved":q.tolist(),"cells":cells,
        "configuration":{"cells":len(q),"length_m":length,"duration_s":duration,
                         "conductivity_W_m_K":conductivity,"cfl":cfl,"flux_scheme":flux_scheme,"boundary":"periodic"},
        "diagnostics":{"steps":steps,"elapsed_s":elapsed,"timestep_retries":retries,
                       "maximum_acoustic_courant":maximum_courant,
                       "maximum_thermal_fourier":maximum_fourier,
                       "initial_integrals":initial_integrals.tolist(),
                       "final_integrals":final_integrals.tolist(),
                       "integral_residuals":residual.tolist(),
                       "maximum_relative_conservation_residual":float(relative.max())},
        "limitations":[
            "Synthetic periodic 1D thermal-acoustic case; no 2D gravity/atmosphere coupling.",
            "Conduction coefficient is prescribed synthetic research input, not validated gas transport.",
            "HLLC preserves stationary contacts; moving/general mixture interfaces may still create pressure errors. Rusanov is a more diffusive baseline.",
            "Instantaneous equilibrium; no slip, phase rates, turbulence or field validation.",
            "No viscous momentum exchange; Euler pressure flux provides conservative momentum coupling.",
        ],
        "provenance":provenance(),
    }


def run_thermal_flow(properties=None, **options):
    p = properties or Properties()
    cells = options.pop("cells",8)
    velocity = options.pop("velocity_m_s",0.)
    initial = initialize_profile(p,cells=cells,length_m=options.get("length_m",1.),
                                 velocity_m_s=velocity)
    result = solve_thermal_flow(initial,properties=p,**options)
    result["initial_condition"]="Synthetic smooth periodic H00/ambient source mass-fraction profile at 102500 Pa"
    return result
