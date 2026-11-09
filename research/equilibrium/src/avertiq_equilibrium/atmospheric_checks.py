"""Independent open-boundary budgets and bounded refinement experiments.

The studies here are numerical smoke/refinement evidence, not EEC550 accuracy.
"""
import math
import numpy as np

from .cases import provenance
from .properties import COMPONENTS, Properties


def _integrals(array, length, height):
    q = np.asarray(array, dtype=float)
    if q.ndim != 3 or q.shape[2] != 8 or not np.isfinite(q).all():
        raise RuntimeError("Atmospheric audit requires eight finite conserved columns")
    return q.sum(axis=(0, 1))*length*height/(q.shape[0]*q.shape[1])


def audit_atmospheric_result(result):
    """Recalculate whole-domain conservative budgets from raw cell fields."""
    config = result["configuration"]
    length, height = float(config["length_x_m"]), float(config["height_m"])
    before = _integrals(result["initial_conserved"], length, height)
    after = _integrals(result["final_conserved"], length, height)
    diagnostics = result["diagnostics"]
    boundary = np.asarray(diagnostics["accumulated_boundary_integrals"], dtype=float)
    source = np.zeros(8)
    source[6] = float(diagnostics["accumulated_gravity_momentum_z"])
    residual = after-before-boundary-source
    initial = np.asarray(result["initial_conserved"], dtype=float)
    scale = np.maximum(np.sum(abs(initial), axis=(0, 1))*length*height/(initial.shape[0]*initial.shape[1]), 1.)
    if not np.isfinite(residual).all() or np.max(abs(residual)/scale) > 1e-8:
        raise RuntimeError("Independent atmospheric boundary/source budget failed")
    return {
        "initial_integrals": before.tolist(), "final_integrals": after.tolist(),
        "net_inward_boundary_integrals": boundary.tolist(),
        "gravity_impulse": float(source[6]), "budget_residuals": residual.tolist(),
        "maximum_normalized_budget_residual": float(np.max(abs(residual)/scale)),
    }


def _metrics(result):
    config = result["configuration"]
    q = np.asarray(result["final_conserved"], dtype=float)
    nz, nx = q.shape[:2]
    length, height = float(config["length_x_m"]), float(config["height_m"])
    dx, dz = length/nx, height/nz
    density = q[:, :, :5].sum(axis=2)
    propane = q[:, :, 0]
    inventory = float(propane.sum()*dx*dz)
    x = (np.arange(nx)+.5)*dx
    z = (np.arange(nz)+.5)*dz
    temperatures = np.array([cell["temperature_K"] for cell in result["cells"]])
    pressures = np.array([cell["pressure_Pa"] for cell in result["cells"]]).reshape(nz, nx)
    reference = np.asarray(result["reference"]["pressure_cells_Pa"], dtype=float)
    return {
        "propane_inventory_kg_per_m_depth": inventory,
        "maximum_total_propane_mass_fraction": float(np.max(propane/density)),
        "minimum_temperature_K": float(temperatures.min()),
        "maximum_pressure_perturbation_from_reference_Pa": float(np.max(abs(pressures-reference[:, None]))),
        "propane_centroid_x_m": float((propane*x[None, :]).sum()/propane.sum()) if inventory > 0 else None,
        "propane_centroid_z_m": float((propane*z[:, None]).sum()/propane.sum()) if inventory > 0 else None,
        "steps": int(result["diagnostics"]["steps"]),
        "elapsed_s": float(result["diagnostics"]["elapsed_s"]),
        "maximum_normalized_budget_residual": audit_atmospheric_result(result)["maximum_normalized_budget_residual"],
    }


def run_refinement():
    """Execute matched-domain/time grid runs and a genuine smaller-step control.

    All grids are deliberately coarse relative to the source window. Differences
    are reported, not converted into an unearned convergence or accuracy claim.
    """
    from .atmospheric import run_atmospheric
    from .eec550_case import build_eec550_case
    props = Properties()
    case = build_eec550_case()
    duration = .001
    grids = (4, 8, 12)
    results = []
    for cells in grids:
        results.append(run_atmospheric(props, nx=cells, nz=cells, duration_s=duration,
                                       cfl=.2, case_config=case))
    fine_times = [run_atmospheric(props, nx=4, nz=4, duration_s=duration,
                                   cfl=value, case_config=case) for value in (.1,.05)]
    fine_time = fine_times[0]
    baseline = results[0]
    metrics = [_metrics(result) for result in results]
    time_metrics_all = [_metrics(result) for result in fine_times]
    time_metrics = time_metrics_all[0]
    if (metrics[0]["steps"] < 2 or time_metrics["steps"] <= metrics[0]["steps"]
            or time_metrics_all[1]["steps"] <= time_metrics["steps"]):
        raise RuntimeError("Time refinement did not produce a nontrivial increase in step count")
    if any(not math.isclose(m["elapsed_s"], duration, abs_tol=1e-12) for m in metrics+time_metrics_all):
        raise RuntimeError("Refinement cases did not end at the same physical time")
    initial_reference = np.asarray(baseline["initial_conserved"])
    if any(not np.array_equal(initial_reference,np.asarray(run["initial_conserved"])) for run in fine_times):
        raise RuntimeError("Time-refinement initial conditions differ")
    base_q = np.asarray(baseline["final_conserved"])
    time_q = np.asarray(fine_time["final_conserved"])
    mean_absolute_change = np.mean(abs(time_q-base_q), axis=(0, 1))
    relative_change = mean_absolute_change/np.maximum(np.mean(abs(base_q), axis=(0, 1)), 1e-12)
    temporal_pairs = []
    all_time_runs = [baseline]+fine_times
    for coarse_cfl,fine_cfl,coarse,fine in zip((.2,.1),(.1,.05),all_time_runs,all_time_runs[1:]):
        cq = np.asarray(coarse["final_conserved"])
        fq = np.asarray(fine["final_conserved"])
        change = np.mean(abs(fq-cq),axis=(0,1))
        relative = change/np.maximum(np.mean(abs(cq),axis=(0,1)),1e-12)
        temporal_pairs.append({"coarse_cfl":coarse_cfl,"fine_cfl":fine_cfl,
            "mean_absolute_change_by_column":change.tolist(),
            "relative_L1_change_by_column":relative.tolist()})
    source_height = float(case["source"]["height_m"])
    height = float(baseline["configuration"]["height_m"])
    rows = []
    for grid, metric in zip(grids, metrics):
        rows.append({"nx":grid, "nz":grid, "cfl":.2,
                     "source_window_height_in_cells": source_height/(height/grid),
                     "metrics":metric})
    return {
        "schema_version":1, "completed":True,"field_comparison_ready":False,
        "scope":"Conditional 2D EEC550-inspired slab smoke refinement, not field validation or demonstrated grid convergence.",
        "matched_duration_s":duration, "grid_cases":rows,
        "time_step_refinement":{
            "nx":4, "nz":4, "baseline_cfl":.2, "smaller_step_cfl":.1,
            "baseline_metrics":metrics[0], "smaller_step_metrics":time_metrics,
            "column_names":baseline["column_names"],
            "mean_absolute_conservative_change":mean_absolute_change.tolist(),
            "relative_L1_conservative_change":relative_change.tolist(),
            "relative_scale_floor":1e-12,
            "performed_with_different_step_counts":True,
            "additional_smaller_step_metrics":time_metrics_all[1],
            "cfl_sequence":[.2,.1,.05],
            "step_count_sequence":[metrics[0]["steps"],time_metrics["steps"],time_metrics_all[1]["steps"]],
            "pairwise_conservative_changes":temporal_pairs,
        },
        "interpretation":[
            "A conserved inventory may agree across grids while the field remains unresolved.",
            "Source-window overlap is exact, but no grid here necessarily resolves the vertical source profile.",
            "Peak concentrations and source-adjacent temperatures are descriptive mesh sensitivities.",
            "This is not a 150 s average, sensor comparison, turbulence calibration or accuracy certificate.",
            "The 2D slab omits lateral spreading and crosswind; finite-width EEC550 validation requires additional modelling.",
        ],
        "spatial_convergence_status":"not_established_source_window_underresolved",
        "time_convergence_status":"not_established_three_CFL_sensitivity_only",
        "grid_runs":results,"additional_time_step_runs":fine_times,
        "case":case, "provenance":provenance(),
    }


def run_atmospheric_checks():
    """Execute short open-boundary/source controls with independent ledgers."""
    from .atmospheric import run_atmospheric, initialize_atmospheric, choose_open_ghost
    from .thermal2d import solve_thermal2d
    from .eec550_case import build_eec550_case, neutral_wind_at_height, source_face_overlaps
    from .equilibrium import Equilibrium
    from .study import build_source, ambient_stream
    props = Properties()
    case = build_eec550_case()
    checks = []
    def bounded(name, measured, tolerance, units):
        value = float(measured)
        passed = bool(math.isfinite(value) and abs(value) <= tolerance)
        checks.append({"name":name,"measured":value,"maximum_absolute":float(tolerance),
                       "units":units,"passed":passed})
        if not passed:
            raise RuntimeError(f"Atmospheric check failed: {name}: {value}")
    def positive(name, measured, minimum, units):
        value = float(measured)
        passed = bool(math.isfinite(value) and value > minimum)
        checks.append({"name":name,"measured":value,"must_exceed":float(minimum),
                       "units":units,"passed":passed})
        if not passed:
            raise RuntimeError(f"Atmospheric check failed: {name}: {value}")

    # Verify weather convention independently of the supplied helper.
    a = case["atmosphere"]
    projection = math.cos(math.radians(a["wind_projection_angle_deg"]))
    expected = a["wind_reference_speed_m_s"]*projection
    bounded("projected wind at recorded reference height",
            neutral_wind_at_height(6.,case)-expected,1e-12,"m/s")
    expected_ustar = .4*2.73/math.log((6.+.006)/.006)
    bounded("neutral friction velocity follows selected U6",a["friction_velocity_m_s"]-expected_ustar,
            1e-12,"m/s")

    # Exact geometric integrals, rather than matching the source to cell centres.
    source = case["source"]
    height = float(case["domain"]["height_m"])
    width = float(source["width_m"])
    source_rates = []
    for nz in (4,8,12):
        dz = height/nz
        faces = np.arange(nz+1)*dz
        overlap = source_face_overlaps(faces.tolist(),case)
        lengths = np.asarray(overlap["overlap_lengths_m"])
        centres = np.asarray(overlap["overlap_centres_m"])
        bounded(f"grid {nz} exact source height",lengths.sum()-source["height_m"],1e-12,"m")
        bounded(f"grid {nz} exact source first vertical moment",
                float(lengths@centres)-source["height_m"]*source["centre_height_m"],1e-12,"m2")
        rate = source["density_kg_m3"]*source["speed_m_s"]*float(lengths.sum())
        propane = rate*source["component_mass_fractions"]["C3"]
        bounded(f"grid {nz} nominal propane per unit depth",
                propane-3./width,1e-10,"kg/(m s)")
        energy_rate = source["density_kg_m3"]*source["speed_m_s"]*float(lengths @ (source["thermal_enthalpy_J_kg"]+.5*source["speed_m_s"]**2+9.81*centres))
        expected_energy = source["per_depth"]["enthalpy_plus_kinetic_W_m"]+source["per_depth"]["potential_energy_W_m"]
        bounded(f"grid {nz} source enthalpy/kinetic/potential integral",energy_rate-expected_energy,1e-7,"W/m")
        source_rates.append({"nz":nz,"height_m":float(lengths.sum()),"energy_W_m":energy_rate,
                             "propane_kg_m_s":float(propane)})

    duration = 1e-4
    ambient = run_atmospheric(props,nx=4,nz=4,duration_s=duration,cfl=.2,
                               case_config=case,source_enabled=False)
    injected = run_atmospheric(props,nx=4,nz=4,duration_s=duration,cfl=.2,
                                case_config=case,source_enabled=True)
    before = np.asarray(ambient["initial_conserved"])
    after = np.asarray(ambient["final_conserved"])
    background_drift = float(np.max(abs(after-before)/np.maximum(abs(before),1.)))
    bounded("open log-wind hydrostatic background preservation",background_drift,1e-10,"normalized state")

    # A real outgoing tracer pulse starts at the rightmost cells. It is not a
    # reflection coefficient test and makes no nonreflecting boundary claim.
    initial, reference, boundary = initialize_atmospheric(props,nx=4,nz=4,
        case_config=case,source_enabled=False)
    source_state = build_source(props).state
    ambient_state = ambient_stream(props)
    source_n = source_state.component_amounts()/source_state.mass_kg
    source_h = source_state.enthalpy_J/source_state.mass_kg
    eq = Equilibrium(props)
    g = 9.81
    dz = height/4
    for j in range(4):
        old = initial[j,-1].copy()
        old_rho = float(old[:5].sum())
        velocity = old[5]/old_rho
        fraction = .002
        n = fraction*source_n+(1-fraction)*ambient_state.mol_per_kg
        h = fraction*source_h+(1-fraction)*ambient_state.enthalpy_J_kg
        state = eq.ph(float(reference["pressure_cells_Pa"][j]),n,h)
        rho = state.mass_kg/state.volume_m3
        internal = state.enthalpy_J/state.mass_kg-state.pressure_Pa/rho
        z = (j+.5)*dz
        initial[j,-1,:5] = rho*n*props.mw
        initial[j,-1,5] = rho*velocity
        initial[j,-1,6] = 0.
        initial[j,-1,7] = rho*(internal+.5*velocity**2+g*z)
    options = dict(properties=props,length_x_m=case["domain"]["length_x_m"],
                   height_m=height,gravity_m_s2=g,cfl=.2,conductivity_W_m_K=0.)
    outgoing = solve_thermal2d(initial,reference=reference,atmosphere=boundary,
                               duration_s=duration,**options)

    # Reverse a physical outlet-side velocity while retaining its internal
    # energy. The Riemann boundary then uses ambient reservoir on backflow.
    backflow_q, backflow_ref, backflow_boundary = initialize_atmospheric(props,nx=4,nz=4,
        case_config=case,source_enabled=False)
    rho = backflow_q[:,-1,:5].sum(axis=1)
    old_u = backflow_q[:,-1,5]/rho
    new_u = -2.*old_u
    backflow_q[:,-1,5] = rho*new_u
    backflow_q[:,-1,7] += .5*rho*(new_u**2-old_u**2)
    incoming = solve_thermal2d(backflow_q,reference=backflow_ref,atmosphere=backflow_boundary,
                              duration_s=1e-5,**options)

    cases = {"ambient":ambient,"source":injected,"outlet_tracer_pulse":outgoing,
             "outlet_backflow":incoming}
    audits = {}
    for label,result in cases.items():
        audit = audit_atmospheric_result(result)
        audits[label] = audit
        cfg = result["configuration"]
        time = float(result["diagnostics"]["elapsed_s"])
        domain_initial_mass = float(np.sum(audit["initial_integrals"][:5]))
        accumulated = np.zeros(8)
        independently_integrated_gravity = 0.
        elapsed = 0.
        side_sums = {side:np.zeros(8) for side in ("left","right","bottom","top")}
        history = result["atmospheric"]["boundary_history"]
        for entry in history:
            dt = float(entry["dt_s"])
            positive(label+" positive accepted dt",dt,0.,"s")
            current_mass = domain_initial_mass+float(accumulated[:5].sum())
            independently_integrated_gravity -= float(cfg["gravity_m_s2"])*current_mass*dt
            net = np.asarray(entry["net_inward_boundary_increment"])
            per_side = entry["per_side_inward_increment"]
            side_net = sum((np.asarray(per_side[side]) for side in side_sums),np.zeros(8))
            bounded(label+" per-step side/net ledger",np.max(abs(net-side_net)),1e-8,"mixed SI flux integral")
            for side in side_sums:side_sums[side]+=np.asarray(per_side[side])
            accumulated += net
            elapsed += dt
        bounded(label+" accepted time ledger",elapsed-time,1e-12,"s")
        bounded(label+" boundary history matches solver",np.max(abs(accumulated-np.asarray(audit["net_inward_boundary_integrals"]))),
                1e-7,"mixed SI flux integral")
        bounded(label+" gravity from independently reconstructed mass history",
                independently_integrated_gravity-audit["gravity_impulse"],1e-8,"kg/s per metre depth")
        residual = np.asarray(audit["budget_residuals"])
        for i,name in enumerate(COMPONENTS):
            bounded(label+" component boundary/source budget "+name,residual[i],1e-8,"kg per metre depth")
        bounded(label+" horizontal momentum budget",residual[5],1e-6,"kg/s per metre depth")
        bounded(label+" vertical wall/open/gravity momentum budget",residual[6],1e-6,"kg/s per metre depth")
        bounded(label+" total energy with potential boundary budget",residual[7],1e-5,"J per metre depth")
        for side, values in side_sums.items():
            expected_side = np.asarray(result["atmospheric"]["per_side_accumulated_inward_integrals"][side])
            bounded(label+" accumulated side ledger "+side,np.max(abs(values-expected_side)),1e-7,"mixed SI flux integral")

    # Independent thermodynamic reconstruction from raw conserved cells.
    for label,result in cases.items():
        q = np.asarray(result["final_conserved"],dtype=float)
        cfg = result["configuration"]
        nx,nz = q.shape[1],q.shape[0]
        dz = cfg["height_m"]/nz
        for index,cell in enumerate(result["cells"]):
            j,i = divmod(index,nx)
            row = q[j,i]
            rho = float(row[:5].sum())
            u,w = float(row[5]/rho),float(row[6]/rho)
            internal = float(row[7]/rho-.5*(u*u+w*w)-cfg["gravity_m_s2"]*(j+.5)*dz)
            n = row[:5]/(rho*props.mw)
            phases = cell["phase_mass_fractions"]
            temp = cell["temperature_K"]
            kwargs = {}
            if phases["water_ice"]>0 and phases["water_liquid"]>0:
                tm = props.melting_temperature(cell["pressure_Pa"])
                bounded(label+f" cell {index} melting temperature",temp-tm,1e-6,"K")
                temp=tm
                kwargs={"water_phase":"ice","ice_fraction":phases["water_ice"]/(phases["water_ice"]+phases["water_liquid"])}
            rebuilt = eq.tp(temp,cell["pressure_Pa"],n,**kwargs)
            bounded(label+f" cell {index} volume",rebuilt.volume_m3*rho-1.,2e-8,"relative volume")
            bounded(label+f" cell {index} internal energy",
                    rebuilt.enthalpy_J-rebuilt.pressure_Pa*rebuilt.volume_m3-internal,.02,"J/kg")
            bounded(label+f" cell {index} phase/component density",
                    np.max(abs(rebuilt.component_amounts()*props.mw*rho-row[:5])),1e-9,"kg/m3")

    # Gross source rate includes pressure traction; do not confuse that normal
    # momentum flux with solely advective jet momentum.
    expected_rate = np.zeros(8)
    total_rate = source["total_mass_flow_kg_s"]/width
    for i,name in enumerate(COMPONENTS):
        expected_rate[i] = source["total_component_mass_kg_s"][name]/width
    expected_rate[5] = total_rate*source["speed_m_s"]+source["pressure_Pa"]*source["height_m"]
    expected_rate[7] = total_rate*(source["thermal_enthalpy_J_kg"]+.5*source["speed_m_s"]**2+
                                   g*source["centre_height_m"])
    reported_rate = np.asarray(injected["atmospheric"]["prescribed_source_rate_per_m_depth"])
    bounded("prescribed source gross flux independent physical ledger",np.max(abs(reported_rate-expected_rate)),
            1e-7,"mixed SI flux per metre depth")
    reported_integral = np.asarray(injected["atmospheric"]["accumulated_prescribed_source_per_m_depth"])
    bounded("source accumulated gross flux equals rate times accepted time",
            np.max(abs(reported_integral-expected_rate*duration)),1e-8,"mixed SI flux integral")
    positive("actual prescribed source adds propane",audits["source"]["final_integrals"][0],1e-12,"kg per metre depth")
    positive("open ambient flow exits right boundary",
             -ambient["atmospheric"]["per_side_accumulated_inward_integrals"]["right"][1],1e-10,"N2 kg per metre depth")
    positive("outlet tracer actually exits the domain",
             -outgoing["atmospheric"]["per_side_accumulated_inward_integrals"]["right"][0],1e-12,"C3 kg per metre depth")
    positive("outlet tracer inventory decreases",
             audits["outlet_tracer_pulse"]["initial_integrals"][0]-audits["outlet_tracer_pulse"]["final_integrals"][0],
             1e-12,"C3 kg per metre depth")
    positive("actual right boundary admits backflow mass",
             sum(incoming["atmospheric"]["per_side_accumulated_inward_integrals"]["right"][:5]),
             1e-10,"kg per metre depth")

    # Explicitly exercise the orientation-aware policy separately from the
    # actual flux test; an ambient reservoir does not itself prescribe flux.
    gas = np.asarray(backflow_ref["conserved"][0,-1]).copy()
    reservoir = gas.copy()
    gas[5] = -2.*abs(gas[5])
    ghost, mode = choose_open_ghost(gas,reservoir,5,1)
    if mode != "ambient_reservoir_backflow" or not np.array_equal(ghost,reservoir):
        raise RuntimeError("Backflow reservoir selection failed")
    gas[5] = abs(gas[5])
    ghost, mode = choose_open_ghost(gas,reservoir,5,1)
    if mode != "extrapolated_outflow" or not np.array_equal(ghost,gas):
        raise RuntimeError("Outflow extrapolation selection failed")
    checks.append({"name":"outflow and backflow ghost policy","passed":True})

    return {
        "schema_version":1,"passed":True,
        "scope":"Independent open-boundary/source numerical checks; not nonreflecting-boundary proof or EEC550 field validation.",
        "checks":checks,"case":case,"source_geometry_by_grid":source_rates,
        "background_normalized_drift":background_drift,
        "source_expected_gross_rate_per_m_depth":expected_rate.tolist(),
        "audits":audits,"controls":cases,
        "limitations":[
            "Outflow pulse test establishes actual material exit, not a reflection coefficient.",
            "Backflow uses a prescribed ambient reservoir and its actual Riemann flux, not a claimed fixed incoming rate.",
            "The inlet is a 2D slab with unresolved finite-width and crosswind physics.",
        ],
        "provenance":provenance(),
    }
