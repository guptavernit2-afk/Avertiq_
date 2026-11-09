"""Conservative thermal/gravity and independent reduction regressions."""
from copy import deepcopy
import numpy as np
import pytest
from avertiq_equilibrium.properties import Properties
from avertiq_equilibrium.thermal2d import initialize_thermal2d, solve_thermal2d, run_thermal2d
from avertiq_equilibrium.thermal_flow import initialize_profile, solve_thermal_flow

@pytest.fixture(scope="module")
def props():
    return Properties()

def test_reference_exact_cell_average_hydrostatic(props):
    q,ref=initialize_thermal2d(props,blob=False)
    rho=q[:,:,:5].sum(2)
    dz=.25
    np.testing.assert_allclose((ref["pressure_faces_Pa"][1:]-ref["pressure_faces_Pa"][:-1])/dz,
                               -rho[:,0]*9.81,rtol=1e-11,atol=1e-10)
    np.testing.assert_allclose(rho[:,0],ref["density_cells_kg_m3"],rtol=1e-13)

@pytest.mark.parametrize("gravity",[0.,9.81])
def test_reference_rest_is_preserved(props,gravity):
    q,ref=initialize_thermal2d(props,gravity_m_s2=gravity,blob=False)
    r=solve_thermal2d(q,properties=props,gravity_m_s2=gravity,reference=ref,
                      duration_s=1e-4,conductivity_W_m_K=0.)
    np.testing.assert_allclose(r["final_conserved"],q,rtol=0,atol=1e-9)
    assert max(abs(c["w_m_s"]) for c in r["cells"])<1e-10

def test_composition_contact_rest_without_heat_or_gravity(props):
    r=run_thermal2d(props,gravity_m_s2=0.,conductivity_W_m_K=0.,duration_s=1e-4)
    np.testing.assert_allclose(r["final_conserved"],r["initial_conserved"],rtol=0,atol=1e-8)
    assert max(abs(c["u_m_s"])+abs(c["w_m_s"]) for c in r["cells"])<1e-9

def test_2d_reduces_to_1d_with_transverse_uniform_state(props):
    q1=initialize_profile(props,cells=4,velocity_m_s=1.)
    q2=np.zeros((4,4,8))
    q2[:,:,:5]=q1[None,:,:5]
    q2[:,:,5]=q1[None,:,5]
    q2[:,:,7]=q1[None,:,6]
    a=solve_thermal_flow(q1,properties=props,duration_s=1e-5,conductivity_W_m_K=0.)
    b=solve_thermal2d(q2,properties=props,duration_s=1e-5,conductivity_W_m_K=0.,gravity_m_s2=0.)
    final=np.asarray(b["final_conserved"])
    np.testing.assert_allclose(final[0,:,:5],np.asarray(a["final_conserved"])[:,:5],rtol=1e-10,atol=1e-9)
    np.testing.assert_allclose(final[0,:,5],np.asarray(a["final_conserved"])[:,5],rtol=1e-10,atol=1e-9)
    np.testing.assert_allclose(final[0,:,7],np.asarray(a["final_conserved"])[:,6],rtol=1e-10,atol=1e-8)
    assert abs(final[:,:,6]).max()<1e-8

def test_heat_and_gravity_budget_and_phase_feedback(props):
    q,ref=initialize_thermal2d(props)
    cold=solve_thermal2d(q,properties=props,reference=ref,duration_s=1e-4,conductivity_W_m_K=0.)
    hot=solve_thermal2d(q,properties=props,reference=ref,duration_s=1e-4,conductivity_W_m_K=1000.)
    final=np.asarray(hot["final_conserved"])
    initial=np.asarray(hot["initial_conserved"])
    d=hot["diagnostics"]
    expected=np.asarray(d["initial_integrals"])+np.asarray(d["accumulated_boundary_integrals"])
    expected[6]+=d["accumulated_gravity_momentum_z"]
    np.testing.assert_allclose(d["final_integrals"],expected,rtol=1e-12,atol=1e-9)
    assert abs(d["budget_residuals"][7])<1e-8
    assert final[:,:,6].sum()<0.
    assert max(abs(a["temperature_K"]-b["temperature_K"]) for a,b in zip(hot["cells"],cold["cells"]))>1e-4
    assert max(abs(a["phase_mass_fractions"]["water_ice"]-b["phase_mass_fractions"]["water_ice"])
               for a,b in zip(hot["cells"],cold["cells"]))>1e-10
    # Density evolves from conservative component fluxes; it is not overwritten by PH.
    assert abs(final[:,:,:5].sum(2)-initial[:,:,:5].sum(2)).max()>0
    assert max(abs(c["volume_constraint_relative_residual"]) for c in hot["cells"])<2e-8

def test_axis_transposition_at_zero_gravity(props):
    q1=initialize_profile(props,cells=4)
    q=np.zeros((4,4,8))
    values=(q1[:,None,:]+q1[None,:,:])/2
    q[:,:,:5]=values[:,:,:5]
    q[:,:,7]=values[:,:,6]
    r=solve_thermal2d(q,properties=props,gravity_m_s2=0.,duration_s=1e-4,conductivity_W_m_K=100.)
    final=np.asarray(r["final_conserved"])
    np.testing.assert_allclose(final[:,:,:5],final[:,:,:5].transpose(1,0,2),rtol=1e-10,atol=1e-9)
    np.testing.assert_allclose(final[:,:,5],final[:,:,6].T,rtol=1e-8,atol=1e-8)
    np.testing.assert_allclose(final[:,:,7],final[:,:,7].T,rtol=1e-10,atol=1e-7)

def test_zero_time_and_no_overwrite(props):
    q,ref=initialize_thermal2d(props)
    copy=q.copy()
    r=solve_thermal2d(q,properties=props,reference=ref,duration_s=0.)
    np.testing.assert_array_equal(r["final_conserved"],q)
    np.testing.assert_array_equal(q,copy)

@pytest.mark.parametrize("option,value",[
    ("gravity_m_s2",-1.),("duration_s",float("nan")),("cfl",.9),
    ("conductivity_W_m_K",-1.),("height_m",0.)])
def test_bad_controls_fail(props,option,value):
    q,_=initialize_thermal2d(props)
    with pytest.raises(ValueError):
        solve_thermal2d(q,properties=props,**{option:value})

def test_reference_cannot_be_arbitrary_frozen_state(props):
    q,ref=initialize_thermal2d(props)
    bad=deepcopy(ref)
    bad["conserved"][0,0,7]+=100.
    with pytest.raises(ValueError,match="declared"):
        solve_thermal2d(q,properties=props,reference=bad)

def test_malformed_or_negative_conserved_cells_fail(props):
    q,_=initialize_thermal2d(props)
    q[0,0,0]=-1.
    with pytest.raises(ValueError):
        solve_thermal2d(q,properties=props)
    with pytest.raises(ValueError):
        solve_thermal2d(np.zeros((3,4,8)),properties=props)


def test_2d_caloric_reference_shift_preserves_coupled_evolution(props):
    offset=1000.  # J/mol propane, carried by every phase consistently.
    class Shifted:
        def __getattr__(self,name):
            return getattr(props,name)
        def gas_h(self,t,i):
            return props.gas_h(t,i)+(offset if i==0 else 0.)
        def condensed(self,t,p,i,phase):
            h,g,v=props.condensed(t,p,i,phase)
            shift=offset if i==0 else 0.
            return h+shift,g+shift,v
    q,ref=initialize_thermal2d(props)
    shifted=q.copy()
    shifted[:,:,7]+=q[:,:,0]/props.mw[0]*offset
    # The isothermal reference contains no propane; its energy is unchanged.
    ordinary=solve_thermal2d(q,properties=props,reference=ref,duration_s=1e-4,
                              conductivity_W_m_K=1000.)
    changed=solve_thermal2d(shifted,properties=Shifted(),reference=ref,duration_s=1e-4,
                             conductivity_W_m_K=1000.)
    for key,atol in [('temperature_K',1e-5),('pressure_Pa',.01),
                     ('u_m_s',1e-6),('w_m_s',1e-6),('density_kg_m3',1e-8)]:
        np.testing.assert_allclose([c[key] for c in ordinary['cells']],
                                   [c[key] for c in changed['cells']],rtol=1e-8,atol=atol)
    for phase in ['gas','propane_liquid','water_liquid','water_ice']:
        np.testing.assert_allclose([c['phase_mass_fractions'][phase] for c in ordinary['cells']],
                                   [c['phase_mass_fractions'][phase] for c in changed['cells']],
                                   rtol=1e-6,atol=1e-8)
