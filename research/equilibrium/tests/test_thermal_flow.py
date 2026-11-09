"""Conservative flux, physical coupling and admissibility tests."""
import numpy as np
import pytest

from avertiq_equilibrium.properties import Properties, PROPANE
from avertiq_equilibrium.thermal_flow import (
    conservative_flux, initialize_profile, solve_thermal_flow, run_thermal_flow)


@pytest.fixture(scope="module")
def props():
    return Properties()


def test_pressure_work_and_momentum_flux_include_pressure():
    q = np.array([[.1,.2,.3,.4,.5,3.,-200.]])
    result = conservative_flux(q,np.array([2.]),np.array([100.]))
    np.testing.assert_allclose(result[0,:5],2*q[0,:5])
    assert result[0,5] == 106.
    assert result[0,6] == -200.  # (rho E + p) u, negative reference energy valid


def test_uniform_rest_remains_uniform_without_spurious_heat_or_motion(props):
    q = np.tile(initialize_profile(props,cells=4)[0],(4,1))
    result = solve_thermal_flow(q,properties=props,duration_s=1e-4,conductivity_W_m_K=1000.)
    np.testing.assert_allclose(result["final_conserved"],q,rtol=0,atol=1e-9)
    assert result["diagnostics"]["maximum_relative_conservation_residual"] < 1e-12


def test_periodic_species_momentum_total_energy_and_volume_constraints(props):
    result = run_thermal_flow(props,duration_s=3e-4)
    initial = np.array(result["initial_conserved"])
    final = np.array(result["final_conserved"])
    np.testing.assert_allclose(final.sum(axis=0),initial.sum(axis=0),rtol=1e-12,atol=1e-9)
    assert any(abs(c["velocity_m_s"])>1e-8 for c in result["cells"])
    assert max(abs(c["volume_constraint_relative_residual"]) for c in result["cells"])<2e-8
    assert all(abs(sum(c["phase_mass_fractions"].values())-1)<1e-10 for c in result["cells"])
    assert result["diagnostics"]["maximum_acoustic_courant"] <= .3+1e-12


def test_heat_conduction_redistributes_energy_without_changing_total(props):
    initial = initialize_profile(props)
    adiabatic = solve_thermal_flow(initial,properties=props,duration_s=1e-5,conductivity_W_m_K=0)
    heated = solve_thermal_flow(initial,properties=props,duration_s=1e-5,conductivity_W_m_K=1000.)
    a=np.array(adiabatic["final_conserved"]);b=np.array(heated["final_conserved"])
    assert np.max(abs(a[:,6]-b[:,6])) > .01
    np.testing.assert_allclose(a[:,:6],b[:,:6],rtol=0,atol=1e-10)
    assert abs(a[:,6].sum()-b[:,6].sum())<1e-8
    assert max(abs(x["phase_mass_fractions"]["water_ice"]-y["phase_mass_fractions"]["water_ice"])
               for x,y in zip(adiabatic["cells"],heated["cells"]))>1e-10


def test_zero_duration_is_identity(props):
    q=initialize_profile(props,cells=4)
    result=solve_thermal_flow(q,properties=props,duration_s=0)
    assert result["diagnostics"]["steps"]==0
    np.testing.assert_array_equal(result["final_conserved"],q)


@pytest.mark.parametrize("option,value", [
    ("length_m",0),("duration_s",-1),("conductivity_W_m_K",-1),
    ("conductivity_W_m_K",float("nan")),("cfl",.8),("cfl",True)])
def test_invalid_numerical_controls_fail(props,option,value):
    q=initialize_profile(props,cells=4)
    with pytest.raises(ValueError):
        solve_thermal_flow(q,properties=props,**{option:value})


def test_malformed_or_negative_species_fail(props):
    q=initialize_profile(props,cells=4)
    q[0,0]=-1e-4
    with pytest.raises(ValueError):
        solve_thermal_flow(q,properties=props)
    with pytest.raises(ValueError):
        solve_thermal_flow(np.zeros((3,7)),properties=props)


def test_energy_reference_shift_does_not_change_evolution(props):
    offset=1000.
    class Shifted:
        def __getattr__(self,name):
            return getattr(props,name)
        def gas_h(self,t,i):
            return props.gas_h(t,i)+(offset if i==PROPANE else 0)
        def condensed(self,t,p,i,phase):
            h,g,v=props.condensed(t,p,i,phase)
            shift=offset if i==PROPANE else 0.
            return h+shift,g+shift,v
    q=initialize_profile(props,cells=4)
    shifted=q.copy()
    shifted[:,6]+=q[:,PROPANE]/props.mw[PROPANE]*offset
    ordinary=solve_thermal_flow(q,properties=props,duration_s=1e-5,conductivity_W_m_K=1000.,flux_scheme="rusanov")
    changed=solve_thermal_flow(shifted,properties=Shifted(),duration_s=1e-5,conductivity_W_m_K=1000.,flux_scheme="rusanov")
    np.testing.assert_allclose([c["temperature_K"] for c in ordinary["cells"]],
                               [c["temperature_K"] for c in changed["cells"]],rtol=0,atol=1e-5)
    np.testing.assert_allclose([c["pressure_Pa"] for c in ordinary["cells"]],
                               [c["pressure_Pa"] for c in changed["cells"]],rtol=0,atol=.01)


def test_hllc_smooth_stationary_material_profile_is_preserved(props):
    q = initialize_profile(props)
    r = solve_thermal_flow(q,properties=props,conductivity_W_m_K=0,duration_s=3e-4)
    np.testing.assert_allclose(r["final_conserved"],q,rtol=0,atol=1e-8)
    assert max(abs(c["velocity_m_s"]) for c in r["cells"]) < 1e-8
    assert max(abs(c["pressure_Pa"]-102500.) for c in r["cells"]) < 1e-3


def test_hllc_sharp_stationary_composition_contact(props):
    from avertiq_equilibrium.study import build_source, ambient_stream
    from avertiq_equilibrium.equilibrium import Equilibrium
    source=build_source(props).state
    ambient=ambient_stream(props)
    warm=Equilibrium(props).ph(102500.,ambient.mol_per_kg,ambient.enthalpy_J_kg)
    def conserved(state):
        rho=state.mass_kg/state.volume_m3
        return np.r_[state.component_amounts()*props.mw/state.volume_m3,
                     0.,state.enthalpy_J/state.volume_m3-102500.]
    q=np.vstack([conserved(source)]*4+[conserved(warm)]*4)
    r=solve_thermal_flow(q,properties=props,conductivity_W_m_K=0,duration_s=3e-4)
    np.testing.assert_allclose(r["final_conserved"],q,rtol=0,atol=1e-8)
    assert max(abs(c["velocity_m_s"]) for c in r["cells"]) < 1e-8
    assert max(abs(c["pressure_Pa"]-102500.) for c in r["cells"]) < 1e-3


def test_hllc_equal_pressure_velocity_flux_upwinds_material_contact(props):
    from avertiq_equilibrium.thermal_flow import interface_flux
    q=initialize_profile(props,velocity_m_s=1.)
    u=np.ones(len(q));pressure=np.full(len(q),102500.);sound=np.full(len(q),300.)
    np.testing.assert_allclose(interface_flux(q,u,pressure,sound),
                               conservative_flux(q,u,pressure),rtol=1e-12,atol=1e-8)


def test_rusanov_retained_as_diffusive_baseline(props):
    q=initialize_profile(props)
    r=solve_thermal_flow(q,properties=props,conductivity_W_m_K=0,flux_scheme="rusanov")
    assert max(abs(c["pressure_Pa"]-102500.) for c in r["cells"]) > .1
    assert r["diagnostics"]["maximum_relative_conservation_residual"] < 1e-10


def test_invalid_flux_scheme_is_rejected(props):
    with pytest.raises(ValueError):
        solve_thermal_flow(initialize_profile(props,cells=4),properties=props,flux_scheme="unknown")
