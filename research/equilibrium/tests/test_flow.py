"""Variable-density hydrodynamic numerical checks, not field validation."""
import numpy as np
import pytest

from avertiq_equilibrium.flow import (
    divergence,project_velocity,advect_fraction,simulate_flow,run_flow)


def test_variable_coefficient_projection():
    rng=np.random.default_rng(4)
    rho=rng.uniform(.8,2.5,(8,10))
    u=rng.normal(size=rho.shape);w=rng.normal(size=(9,10));w[[0,-1]]=0
    up,wp,p,audit=project_velocity(u,w,rho,.3,.2,.01)
    assert np.max(np.abs(divergence(up,wp,.3,.2)))<1e-10
    assert audit["relative_pressure_residual"]<1e-10
    assert p[0,0]==0
    assert np.all(wp[[0,-1]]==0)
    rx=.5*(rho+np.roll(rho,1,axis=1));rz=.5*(rho[1:]+rho[:-1])
    before=float((rx*u*u).sum()+(rz*w[1:-1]**2).sum())
    after=float((rx*up*up).sum()+(rz*wp[1:-1]**2).sum())
    assert after<=before+1e-10  # Weighted projection cannot add kinetic energy.


def test_constant_velocity_and_fraction_preserved():
    rho=np.full((8,10),1.4);u=np.full_like(rho,2.);w=np.zeros((9,10))
    up,wp,_,_=project_velocity(u,w,rho,1.,1.,.1)
    np.testing.assert_allclose(up,u)
    np.testing.assert_allclose(wp,w)
    a=advect_fraction(np.full_like(rho,.4),up,wp,1.,1.,.1)
    np.testing.assert_allclose(a,.4,atol=1e-14)


def test_conservative_fraction_periodic_shift():
    a=np.zeros((8,10));a[:,2:4]=1.
    moved=advect_fraction(a,np.ones_like(a),np.zeros((9,10)),1.,1.,1.)
    np.testing.assert_allclose(moved,np.roll(a,1,axis=1))
    assert moved.sum()==a.sum()


def test_stratified_hydrostatic_rest():
    a=np.tile(np.linspace(.8,.1,12)[:,None],(1,12))
    result=simulate_flow(a,duration_s=.05)
    assert np.max(np.abs(result["u_face_m_s"]))<1e-10
    assert np.max(np.abs(result["w_face_m_s"]))<1e-10
    np.testing.assert_allclose(result["final_fraction"],a,atol=1e-13)


def test_equal_density_remains_at_rest_under_gravity():
    rng=np.random.default_rng(5);a=rng.uniform(0,1,(8,8))
    r=simulate_flow(a,rho_light=1.2,rho_heavy=1.2,duration_s=.05)
    np.testing.assert_allclose(r["final_fraction"],a,atol=1e-13)
    assert np.max(np.abs(r["w_face_m_s"]))<1e-12


def _blob(n=16):
    x=(np.arange(n)+.5)*10/n;z=x.copy()
    return .8*np.exp(-((x[None,:]-5)**2+(z[:,None]-6)**2)/(2*.9**2))


def test_heavy_blob_sinks_and_zero_gravity_stays():
    a=_blob()
    heavy=simulate_flow(a,duration_s=.15)
    control=simulate_flow(a,duration_s=.15,gravity_m_s2=0)
    d=heavy["diagnostics"]
    assert d["final_dense_centroid_z_m"]<d["initial_dense_centroid_z_m"]-1e-4
    np.testing.assert_allclose(control["final_fraction"],a,atol=1e-14)
    assert d["relative_mass_residual"]<1e-12
    assert d["max_divergence_s_inv"]<1e-10


def test_light_blob_rises():
    light_fraction=_blob()
    result=simulate_flow(1-light_fraction,duration_s=.15)
    z=(np.arange(16)+.5)*10/16
    initial=float((light_fraction*z[:,None]).sum()/light_fraction.sum())
    final_light=1-np.array(result["final_fraction"])
    final=float((final_light*z[:,None]).sum()/final_light.sum())
    assert final>initial+1e-4


def test_endpoint_flow_record():
    result=run_flow(nx=8,nz=8,duration_s=.1)
    assert result["configuration"]["rho_heavy_kg_m3"]>result["configuration"]["rho_light_kg_m3"]
    assert not result["field_prediction_ready"]
    assert result["diagnostics"]["relative_mass_residual"]<1e-12
    assert "provenance" in result


@pytest.mark.parametrize("kwargs",[
    {"duration_s":-1},{"gravity_m_s2":float("nan")},
    {"rho_light":0},{"rho_heavy":.5},{"viscosity_m2_s":-1}])
def test_invalid_flow_inputs(kwargs):
    with pytest.raises(ValueError):
        simulate_flow(np.full((8,8),.4),**kwargs)


def test_fraction_instability_is_refused():
    a=np.full((8,8),.4)
    with pytest.raises(ValueError,match="CFL"):
        advect_fraction(a,np.ones_like(a)*2,np.zeros((9,8)),1.,1.,1.)
