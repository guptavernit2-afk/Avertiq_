"""Analytic scalar transport checks and conservative equilibrium coupling."""
import numpy as np
import pytest
from avertiq_equilibrium.transport import solve_scalar, run_transport


def test_uniform_state_is_exact_and_periodic_mass_is_conserved():
    result = solve_scalar(np.full(64,.3), velocity_m_s=-2.,duration_s=4.)
    np.testing.assert_array_equal(result["final_fraction"],np.full(64,.3))
    assert result["diagnostics"]["relative_scalar_mass_residual"] < 1e-12


@pytest.mark.parametrize("velocity",[-1.,1.])
def test_unit_courant_advection_is_exact_cell_shift(velocity):
    initial = np.array([0.,.1,.7,.5,0.,0.,0.,0.])
    r=solve_scalar(initial,length_m=8.,velocity_m_s=velocity,diffusivity_m2_s=0.,duration_s=1.,cfl=1.)
    np.testing.assert_allclose(r["final_fraction"],np.roll(initial,int(velocity)),atol=1e-15)


def test_diffusion_matches_periodic_analytic_decay():
    n=128; length=20.; k=2*np.pi/length; diffusion=.2; t=3.
    x=(np.arange(n)+.5)*length/n
    initial=.5+.2*np.cos(k*x)
    r=solve_scalar(initial,length_m=length,velocity_m_s=0.,diffusivity_m2_s=diffusion,duration_s=t)
    exact=.5+.2*np.exp(-diffusion*k*k*t)*np.cos(k*x)
    assert np.max(abs(np.asarray(r["final_fraction"])-exact)) < 1e-5


def test_advection_diffusion_converges_under_refinement():
    errors=[]
    for n in [40,80,160]:
        length=20.; k=2*np.pi/length; u=.7; d=.1; t=2.
        x=(np.arange(n)+.5)*length/n
        r=solve_scalar(.5+.2*np.cos(k*x),length_m=length,velocity_m_s=u,diffusivity_m2_s=d,duration_s=t)
        exact=.5+.2*np.exp(-d*k*k*t)*np.cos(k*(x-u*t))
        errors.append(np.sqrt(np.mean((np.asarray(r["final_fraction"])-exact)**2)))
    assert errors[1]<.7*errors[0] and errors[2]<.7*errors[1]


def test_sharp_pulse_remains_bounded_without_clipping():
    r=solve_scalar([0,0,1,1,0,0,0,0],length_m=8.,velocity_m_s=-1.,diffusivity_m2_s=.2,duration_s=20.)
    assert min(r["final_fraction"])>=0 and max(r["final_fraction"])<=1
    assert abs(sum(r["final_fraction"])-2)<1e-12
    assert r["numerics"]["positivity_weight_sum"]<=.8+1e-12


@pytest.mark.parametrize("kwargs",[
 {"length_m":0},{"velocity_m_s":float("nan")},{"diffusivity_m2_s":-.1},
 {"duration_s":-1},{"cfl":1.1},{"cfl":0},{"length_m":True},
])
def test_invalid_config_fails(kwargs):
    with pytest.raises(ValueError):solve_scalar([0,.1,.2,0],**kwargs)


@pytest.mark.parametrize("initial",[[0,1],[0,float("inf"),0,0],[0,1.1,0,0],[0,-.1,0,0]])
def test_invalid_field_fails(initial):
    with pytest.raises(ValueError):solve_scalar(initial)


def test_thermodynamic_coupling_preserves_components_and_energy():
    r=run_transport(cells=24,duration_s=4.)
    assert not r["field_prediction_ready"]
    assert r["transport"]["diagnostics"]["passed"]
    assert max(abs(x) for x in r["conservation"]["component_sum_residual_mol_per_kg_cells"].values()) < 1e-10
    assert abs(r["conservation"]["thermal_enthalpy_sum_residual_J_per_kg_cells"]) < 1e-7
    assert r["conservation"]["maximum_local_energy_residual_J_kg"] < 1
    for p in r["equilibrium_cells"]:
        assert sum(p["phase_mass_fractions"].values())==pytest.approx(1.,abs=1e-12)
        assert 0<=p["gas_propane_mole_fraction"]<=1
