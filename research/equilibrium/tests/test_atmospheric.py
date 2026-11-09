"""Open-face policy, baseline preservation and prescribed source geometry."""
import json
import math

import numpy as np
import pytest

from avertiq_equilibrium.atmospheric import (
    choose_open_ghost, initialize_atmospheric, run_atmospheric)
from avertiq_equilibrium.eec550_case import build_eec550_case
from avertiq_equilibrium.properties import Properties

@pytest.fixture(scope="module")
def props():
    return Properties()

def test_open_ghost_changes_only_on_backflow():
    interior=np.zeros(8);interior[1]=1.;interior[5]=2.;interior[7]=-1e5
    ambient=interior.copy();ambient[5]=3.
    ghost,mode=choose_open_ghost(interior,ambient,5,1)
    np.testing.assert_array_equal(ghost,interior)
    assert mode=="extrapolated_outflow"
    interior[5]=-2.
    ghost,mode=choose_open_ghost(interior,ambient,5,1)
    np.testing.assert_array_equal(ghost,ambient)
    assert mode=="ambient_reservoir_backflow"
    ghost[1]=99.
    assert ambient[1]==1.

@pytest.mark.parametrize("bad", [np.zeros(8),np.full(8,float("nan")),np.zeros(7)])
def test_invalid_boundary_states_refused(bad):
    valid=np.zeros(8);valid[1]=1.
    with pytest.raises(ValueError):
        choose_open_ghost(bad,valid,5,1)

def test_top_boundary_switch_uses_vertical_velocity():
    interior=np.zeros(8);interior[1]=1.;interior[5]=50.;interior[6]=-.1
    ambient=interior.copy();ambient[6]=0.
    ghost,mode=choose_open_ghost(interior,ambient,6,1)
    assert mode=="ambient_reservoir_backflow" and ghost[6]==0.

def test_ambient_wind_reference_stays_steady_with_open_throughflow(props):
    report=run_atmospheric(props,source_enabled=False,duration_s=.001)
    before=np.asarray(report["initial_conserved"]);after=np.asarray(report["final_conserved"])
    assert np.max(np.abs(after-before)/np.maximum(np.abs(before),1.))<1e-10
    ledger=report["atmospheric"]["per_side_accumulated_inward_integrals"]
    assert sum(ledger["left"][:5])>0
    assert sum(ledger["right"][:5])<0
    assert report["diagnostics"]["maximum_relative_budget_residual"]<1e-10
    json.dumps(report,allow_nan=False)

def test_source_patch_mass_and_energy_are_grid_independent(props):
    case=build_eec550_case()
    source=case["source"]
    expected_mass=source["total_mass_flow_kg_s"]/source["width_m"]
    expected_propane=source["propane_mass_flow_kg_s"]/source["width_m"]
    expected_energy=expected_mass*(source["thermal_enthalpy_J_kg"]+
                      .5*source["speed_m_s"]**2+9.81*source["centre_height_m"])
    for nz in (4,8,12):
        _,_,boundary=initialize_atmospheric(props,nx=4,nz=nz,case_config=case)
        rate=boundary.gross_source_rate
        assert sum(rate[:5])==pytest.approx(expected_mass,rel=1e-12)
        assert rate[0]==pytest.approx(expected_propane,rel=1e-12)
        assert rate[7]==pytest.approx(expected_energy,rel=1e-12)
        assert sum(boundary.overlap["overlap_lengths_m"])==pytest.approx(source["height_m"])
    # Source is below coarse row centre: exact patch potential must differ.
    coarse_energy=expected_mass*(source["thermal_enthalpy_J_kg"]+
                   .5*source["speed_m_s"]**2+9.81)
    assert abs(coarse_energy-expected_energy)>1.

def test_prescribed_source_and_all_open_faces_close_budget(props):
    result=run_atmospheric(props,duration_s=.001)
    q0=np.asarray(result["initial_conserved"]);q1=np.asarray(result["final_conserved"])
    volume=16.*8./16
    delta=(q1-q0).sum((0,1))*volume
    sides=result["atmospheric"]["per_side_accumulated_inward_integrals"]
    boundary=sum((np.asarray(v) for v in sides.values()),np.zeros(8))
    body=np.zeros(8);body[6]=result["diagnostics"]["accumulated_gravity_momentum_z"]
    np.testing.assert_allclose(delta,boundary+body,rtol=1e-9,atol=1e-7)
    gross=result["atmospheric"]["accumulated_prescribed_source_per_m_depth"]
    assert gross[0]==pytest.approx(3./result["atmospheric"]["case_configuration"]["source"]["width_m"]*.001)
    assert result["field_prediction_ready"] is False


def test_default_runtime_honours_case_numerics_and_live_source(props):
    result=run_atmospheric(props,source_enabled=False)
    numerical=result["atmospheric"]["case_configuration"]["numerics"]
    for actual,key in (("nx","default_nx"),("nz","default_nz"),
                       ("duration_s","smoke_duration_s"),("cfl","cfl"),
                       ("conductivity_W_m_K","conductivity_W_m_K")):
        assert result["configuration"][actual]==numerical[key]
    assert result["atmospheric"]["source_thermodynamic_compatibility"]["passed"]


def test_incompatible_caloric_reference_refused(props):
    class Shifted:
        def __getattr__(self,name):return getattr(props,name)
        def gas_h(self,t,i):return props.gas_h(t,i)+(1000. if i==0 else 0.)
        def condensed(self,t,p,i,phase):
            h,g,v=props.condensed(t,p,i,phase)
            shift=1000. if i==0 else 0.
            return h+shift,g+shift,v
    with pytest.raises(ValueError,match="enthalpy reference"):
        initialize_atmospheric(Shifted())


@pytest.mark.parametrize("nx",[0,True,17])
def test_invalid_grid_refused_before_allocation(props,nx):
    with pytest.raises(ValueError):initialize_atmospheric(props,nx=nx)

def test_reused_boundary_reports_only_the_current_solve(props):
    from avertiq_equilibrium.thermal2d import solve_thermal2d

    initial, _, boundary = initialize_atmospheric(props, nx=4, nz=4)
    options = dict(properties=props, atmosphere=boundary,
                   length_x_m=boundary.lx, height_m=boundary.height)
    pulse = solve_thermal2d(initial, duration_s=.0001, **options)["atmospheric"]
    at_start = solve_thermal2d(initial, duration_s=0., **options)["atmospheric"]

    assert pulse["boundary_history"]
    assert pulse["accumulated_prescribed_source_per_m_depth"][0] > 0
    assert at_start["boundary_history"] == []
    for amounts in at_start["per_side_accumulated_inward_integrals"].values():
        np.testing.assert_array_equal(amounts, np.zeros(8))
    np.testing.assert_array_equal(at_start["accumulated_prescribed_source_per_m_depth"], np.zeros(8))
    np.testing.assert_array_equal(at_start["accumulated_source_excess_over_replaced_ambient_per_m_depth"], np.zeros(8))


@pytest.mark.parametrize("change", ["length_x", "height", "nx", "nz", "gravity"])
def test_open_solver_rejects_incompatible_boundary_geometry(props, change):
    from avertiq_equilibrium.thermal2d import solve_thermal2d

    initial, _, boundary = initialize_atmospheric(props, nx=4, nz=4)
    options = dict(properties=props, atmosphere=boundary, duration_s=0.,
                   length_x_m=boundary.lx, height_m=boundary.height, gravity_m_s2=boundary.g)
    if change == "nx":
        initial = np.repeat(initial, 2, axis=1)
    elif change == "nz":
        initial = np.repeat(initial, 2, axis=0)
    else:
        key = {"length_x":"length_x_m", "height":"height_m", "gravity":"gravity_m_s2"}[change]
        options[key] += 1.
    with pytest.raises(ValueError, match="boundary grid, domain extents and gravity"):
        solve_thermal2d(initial, **options)
