"""Independent budgets, controls and EOS checks for coupled 2D research flow."""
import math
import numpy as np

from .cases import provenance
from .properties import Properties, COMPONENTS
from .equilibrium import Equilibrium
from . import thermal2d


def _integrals(array, length, height):
    q = np.asarray(array, dtype=float)
    if q.ndim != 3 or q.shape[2] != 8 or not np.isfinite(q).all():
        raise RuntimeError("2D checker requires eight finite conservative columns")
    return q.sum(axis=(0, 1))*length*height/(q.shape[0]*q.shape[1])


def run_thermal2d_checks():
    checks = []
    def bounded(name, measured, tolerance, units):
        value = float(measured)
        passed = bool(math.isfinite(value) and abs(value) <= tolerance)
        checks.append({"name":name,"measured":value,"maximum_absolute":tolerance,
                       "units":units,"passed":passed})
        if not passed:
            raise RuntimeError(f"2D thermal check failed: {name}: {value}")
    def positive(name, measured, minimum, units):
        value = float(measured)
        passed = bool(math.isfinite(value) and value > minimum)
        checks.append({"name":name,"measured":value,"must_exceed":minimum,
                       "units":units,"passed":passed})
        if not passed:
            raise RuntimeError(f"2D thermal check failed: {name}: {value}")

    props = Properties()
    tp = Equilibrium(props)
    gravity = 9.81
    duration = 3e-4
    nx = nz = 4
    length = height = 1.
    dz = height/nz
    z = (np.arange(nz)+.5)*dz
    initial, reference = thermal2d.initialize_thermal2d(props,nx=nx,nz=nz,
        gravity_m_s2=gravity)
    reference_q = np.asarray(reference["conserved"])
    faces = np.asarray(reference["pressure_faces_Pa"])
    density_ref = reference_q[:,:,:5].sum(axis=2)
    bounded("hydrostatic reference face pressure/body-force compatibility",
            np.max(abs(np.diff(faces)/dz+gravity*density_ref[:,0])), 1e-7, "Pa/m")
    # The reference is the exact cell-average ideal-gas isothermal profile.
    k = float(reference["metadata"]["density_per_pressure"])
    expected_faces = faces[0]*np.exp(-gravity*k*np.arange(nz+1)*dz)
    bounded("analytic isothermal reference pressure",np.max(abs(faces-expected_faces)),
            1e-7,"Pa")
    options = dict(properties=props,length_x_m=length,height_m=height,
                   gravity_m_s2=gravity,duration_s=duration,reference=reference)
    hydro = thermal2d.solve_thermal2d(reference_q,conductivity_W_m_K=1000.,**options)
    no_heat = thermal2d.solve_thermal2d(initial,conductivity_W_m_K=0.,**options)
    heated = thermal2d.solve_thermal2d(initial,conductivity_W_m_K=1000.,**options)

    # Removing gravity changes the definition of total energy: subtract old rho*g*z.
    # Pressure and all other physical initial fields stay matched. The retained
    # initial hydrostatic pressure gradient is unbalanced without gravity, so this
    # control is not expected to remain at rest.
    zero_q = initial.copy()
    zero_q[:,:,7] -= initial[:,:,:5].sum(axis=2)*gravity*z[:,None]
    uniform_zero, zero_reference = thermal2d.initialize_thermal2d(props,nx=nx,nz=nz,
        gravity_m_s2=0.,blob=False)
    zero_g = thermal2d.solve_thermal2d(zero_q,properties=props,length_x_m=length,
        height_m=height,gravity_m_s2=0.,duration_s=duration,
        conductivity_W_m_K=0.,reference=zero_reference)
    zero_uniform = thermal2d.solve_thermal2d(uniform_zero,properties=props,
        length_x_m=length,height_m=height,gravity_m_s2=0.,duration_s=duration,
        conductivity_W_m_K=1000.,reference=zero_reference)

    hydro_final = np.asarray(hydro["final_conserved"])
    hydro_drift = float(np.max(abs(hydro_final-reference_q)/np.maximum(abs(reference_q),1.)))
    hydro_speed = max(math.hypot(c["velocity_x_m_s"],c["velocity_z_m_s"])
                      for c in hydro["cells"])
    bounded("isothermal hydrostatic conservative rest",hydro_drift,1e-8,"normalized residual")
    bounded("isothermal hydrostatic velocity rest",hydro_speed,1e-7,"m/s")
    bounded("zero-gravity uniform state preserved",
            np.max(abs(np.asarray(zero_uniform["final_conserved"])-uniform_zero)
                   /np.maximum(abs(uniform_zero),1.)),1e-9,"normalized residual")

    cases = {"hydrostatic":hydro,"no_heat":no_heat,"heated":heated,
             "zero_gravity_matched_physical_state":zero_g,"zero_gravity_uniform":zero_uniform}
    originals = {"hydrostatic":reference_q,"no_heat":initial,"heated":initial,
                 "zero_gravity_matched_physical_state":zero_q,"zero_gravity_uniform":uniform_zero}
    for label, result in cases.items():
        before = np.asarray(originals[label])
        after = np.asarray(result["final_conserved"])
        config = result["configuration"]
        g = float(config["gravity_m_s2"])
        t = float(config["duration_s"])
        a, b = _integrals(before,length,height), _integrals(after,length,height)
        for i, component in enumerate(COMPONENTS):
            bounded(label+" component mass "+component,b[i]-a[i],
                    1e-10*max(abs(a[i]),1.),"kg/m depth")
        bounded(label+" horizontal momentum",b[5]-a[5],1e-8,"kg/s per unit depth")
        bounded(label+" total internal kinetic potential energy",b[7]-a[7],
                1e-8*max(abs(a[7]),1.),"J/m depth")
        boundary = np.asarray(result["diagnostics"]["accumulated_boundary_integrals"],dtype=float)
        bounded(label+" closed wall component flux",np.max(abs(boundary[:5])),1e-10,"kg/m depth")
        bounded(label+" adiabatic closed wall energy flux",boundary[7],1e-7,"J/m depth")
        expected_gravity_impulse = -g*float(a[:5].sum())*t
        bounded(label+" integrated body force",
                result["diagnostics"]["accumulated_gravity_momentum_z"]-expected_gravity_impulse,
                1e-9,"kg/s per unit depth")
        bounded(label+" wall traction plus gravity momentum budget",
                b[6]-a[6]-boundary[6]-expected_gravity_impulse,1e-8,"kg/s per unit depth")
        # Stored total E includes potential; changes of gas E must be balanced
        # by changes of rho*g*z, not by another added gravity heat source.
        potential_before=float(np.sum(before[:,:,:5].sum(2)*g*z[:,None])*length*height/(nx*nz))
        potential_after=float(np.sum(after[:,:,:5].sum(2)*g*z[:,None])*length*height/(nx*nz))
        gas_energy_change=(b[7]-potential_after)-(a[7]-potential_before)
        bounded(label+" gas/potential energy exchange",
                gas_energy_change+potential_after-potential_before,1e-6,"J/m depth")
        if len(result["cells"]) != nx*nz:
            raise RuntimeError("2D checker cell count mismatch")
        for index, cell in enumerate(result["cells"]):
            j,i=divmod(index,nx)
            row=after[j,i]
            rho=float(row[:5].sum())
            u,w=float(row[5]/rho),float(row[6]/rho)
            internal=float(row[7]/rho-.5*(u*u+w*w)-g*z[j])
            n=row[:5]/(rho*props.mw)
            phase=cell["phase_mass_fractions"]
            bounded(label+f" cell {index} phase sum",sum(phase.values())-1.,1e-9,"1")
            bounded(label+f" cell {index} conservative internal energy",
                    cell["internal_energy_J_kg"]-internal,1e-6,"J/kg")
            bounded(label+f" cell {index} raw composition",
                    np.max(abs(n-np.array([cell["component_mol_per_kg"][c] for c in COMPONENTS]))),
                    1e-9,"mol/kg")
            kwargs={}
            temp=cell["temperature_K"]
            if phase["water_ice"]>0 and phase["water_liquid"]>0:
                tm=props.melting_temperature(cell["pressure_Pa"])
                bounded(label+f" cell {index} melting temperature",temp-tm,1e-6,"K")
                temp=tm
                kwargs={"water_phase":"ice",
                        "ice_fraction":phase["water_ice"]/(phase["water_ice"]+phase["water_liquid"])}
            rebuilt=tp.tp(temp,cell["pressure_Pa"],n,**kwargs)
            bounded(label+f" cell {index} independent TP volume",rebuilt.volume_m3*rho-1.,
                    2e-8,"relative volume")
            bounded(label+f" cell {index} independent TP internal energy",
                    rebuilt.enthalpy_J-rebuilt.pressure_Pa*rebuilt.volume_m3-internal,.02,"J/kg")
            bounded(label+f" cell {index} phase-component density",
                    np.max(abs(rebuilt.component_amounts()*props.mw*rho-row[:5])),1e-9,"kg/m3")

    temp_response=max(abs(a["temperature_K"]-b["temperature_K"])
                      for a,b in zip(heated["cells"],no_heat["cells"]))
    pressure_response=max(abs(a["pressure_Pa"]-b["pressure_Pa"])
                          for a,b in zip(heated["cells"],no_heat["cells"]))
    phase_response=max(abs(a["phase_mass_fractions"][phase]-b["phase_mass_fractions"][phase])
                       for a,b in zip(heated["cells"],no_heat["cells"])
                       for phase in ("water_ice","water_liquid","propane_liquid"))
    heat_momentum=float(np.max(abs(np.asarray(heated["final_conserved"])[:,:,5:7]
                                  -np.asarray(no_heat["final_conserved"])[:,:,5:7])))
    gravity_response=max(abs(a["velocity_z_m_s"]-b["velocity_z_m_s"])
                         for a,b in zip(no_heat["cells"],zero_g["cells"]))
    positive("heat changes temperature",temp_response,1e-8,"K")
    positive("heat changes EOS pressure",pressure_response,1e-4,"Pa")
    positive("heat changes phase partition",phase_response,1e-12,"mass fraction")
    positive("heat feeds back into momentum",heat_momentum,1e-9,"kg/(m2 s)")
    positive("gravity changes vertical motion for matched physical initial state",
             gravity_response,1e-8,"m/s")

    # Independent dimensional reduction: uniform z, zero gravity, one Euler step.
    from .thermal_flow import initialize_profile,solve_thermal_flow
    q1=initialize_profile(props,cells=4,length_m=1.,velocity_m_s=1.)
    q2=np.zeros((4,4,8));q2[:,:,:5]=q1[None,:,:5]
    q2[:,:,5]=q1[None,:,5];q2[:,:,7]=q1[None,:,6]
    one=solve_thermal_flow(q1,properties=props,duration_s=1e-5,conductivity_W_m_K=10.)
    two=thermal2d.solve_thermal2d(q2,properties=props,gravity_m_s2=0.,
        duration_s=1e-5,conductivity_W_m_K=10.,reference=zero_reference)
    q1_after=np.asarray(one["final_conserved"])
    q2_after=np.asarray(two["final_conserved"])
    mapped=np.concatenate((q2_after[:,:,:6],q2_after[:,:,7,None]),axis=2)
    reduction_error=float(np.max(abs(mapped-q1_after[None,:,:])/np.maximum(abs(q1_after[None,:,:]),1.)))
    bounded("2D reduces to 1D horizontal Euler heat update",reduction_error,1e-8,"normalized residual")
    bounded("1D reduction creates no vertical momentum",np.max(abs(q2_after[:,:,6])),1e-9,"kg/(m2 s)")

    return {"schema_version":1,"passed":True,
        "scope":"Independent numerical verification of tiny 2D compressible equilibrium thermal/gravity flow; not EEC550 or field validation.",
        "checks":checks,"controls":cases,
        "reference_checks":{"hydrostatic_normalized_drift":hydro_drift,
                            "hydrostatic_maximum_speed_m_s":hydro_speed},
        "heat_control_response":{"temperature_K":temp_response,"pressure_Pa":pressure_response,
            "condensate_mass_fraction":phase_response,"momentum_density_kg_m2_s":heat_momentum,
            "conductivity_W_m_K":1000.,"meaning":"Prescribed synthetic stress coefficient, not industrial transport data."},
        "gravity_control_response":{"maximum_vertical_velocity_difference_m_s":gravity_response,
            "meaning":"Matched physical initial fields; gravitational potential convention adjusted. The initial pressure gradient is not balanced in zero gravity, so this is not a rest control."},
        "dimensional_reduction":{"initial_horizontal_velocity_m_s":1.,"normalized_conservative_difference":reduction_error,
            "one_dimensional":one,"two_dimensional":two},
        "provenance":provenance()}
