"""Independent UV identities, pressure bracket and caloric/acoustic checks."""
import math
import numpy as np
import pytest

from avertiq_equilibrium.equilibrium import Equilibrium
from avertiq_equilibrium.equilibrium_uv import EquilibriumUV
from avertiq_equilibrium.properties import Properties, PROPANE
from avertiq_equilibrium.cases import feed
from avertiq_equilibrium.study import ambient_stream


@pytest.fixture(scope="module")
def props():
    return Properties()


def normalized_source(p, dry=False):
    n = feed(p, dry=dry)
    return n/float(n @ p.mw)


@pytest.mark.parametrize("temperature,pressure,dry", [
    (196., 102500., False), (205., 120000., False),
    (195., 110000., True), (285., 80000., False)])
def test_uv_roundtrip(props, temperature, pressure, dry):
    n = normalized_source(props, dry)
    original = Equilibrium(props).tp(temperature, pressure, n)
    rho = original.mass_kg/original.volume_m3
    energy = original.enthalpy_J-pressure*original.volume_m3
    result = EquilibriumUV(props).solve(rho, n, energy)
    assert result.pressure_Pa == pytest.approx(pressure, abs=.01)
    assert result.temperature_K == pytest.approx(temperature, abs=1e-5)
    assert result.volume_m3 == pytest.approx(original.volume_m3, rel=2e-8)
    assert result.enthalpy_J-result.pressure_Pa*result.volume_m3 == pytest.approx(energy, abs=.01)
    np.testing.assert_allclose(result.component_amounts(), n, rtol=1e-10, atol=1e-10)


def test_melting_plateau_uv(props):
    n = normalized_source(props)
    model = Equilibrium(props)
    t = props.melting_temperature(102500.)
    state = model.tp(t, 102500., n, ice_fraction=.5)
    energy = state.enthalpy_J-state.pressure_Pa*state.volume_m3
    found = EquilibriumUV(props).solve(1/state.volume_m3, n, energy)
    assert found.temperature_K == pytest.approx(t, abs=1e-7)
    assert found.ice_mol > 0 and found.water_liquid_mol > 0
    assert found.ice_mol/(found.ice_mol+found.water_liquid_mol) == pytest.approx(.5,abs=1e-7)


def test_dry_ideal_gas_sound_speed_cv_and_derivative_refinement(props):
    n = ambient_stream(props, relative_humidity=0).mol_per_kg
    state = Equilibrium(props).tp(283.05, 102500., n)
    rho = 1/state.volume_m3
    e = state.enthalpy_J-state.pressure_Pa*state.volume_m3
    cp = sum(n[i]*(props.gas_h(283.051,i)-props.gas_h(283.049,i))/.002 for i in range(5))
    gas_r = float(n.sum())*props.r
    cv = cp-gas_r
    expected_c = math.sqrt(cp/cv*state.pressure_Pa/rho)
    uv = EquilibriumUV(props)
    c = uv.sound_speed(rho,n,e,state=state)
    assert c == pytest.approx(expected_c,rel=2e-5)
    assert uv.sound_speed(rho,n,e,state=state,relative_step=5e-5) == pytest.approx(c,rel=1e-5)
    assert uv.heat_capacity_cv(rho,n,e,state=state) == pytest.approx(cv,rel=2e-5)


def test_uv_energy_reference_invariance(props):
    n = normalized_source(props)
    state = Equilibrium(props).tp(210., 102500., n)
    rho = 1/state.volume_m3
    energy = state.enthalpy_J-state.pressure_Pa*state.volume_m3
    offset = 1e5
    class Shifted:
        def __getattr__(self,name):
            return getattr(props,name)
        def gas_h(self,t,i):
            return props.gas_h(t,i)+(offset if i==PROPANE else 0)
        def condensed(self,t,p,i,phase):
            h,g,v = props.condensed(t,p,i,phase)
            shift=offset if i==PROPANE else 0
            return h+shift,g+shift,v
    found = EquilibriumUV(Shifted()).solve(rho,n,energy+offset*n[PROPANE])
    assert found.temperature_K == pytest.approx(state.temperature_K,abs=1e-5)
    assert found.pressure_Pa == pytest.approx(state.pressure_Pa,abs=.01)


@pytest.mark.parametrize("rho,energy", [(0.,0.),(-1.,0.),(float("nan"),0.),(1.,float("inf"))])
def test_invalid_uv_input(props,rho,energy):
    with pytest.raises(ValueError):
        EquilibriumUV(props).solve(rho,normalized_source(props),energy)


def test_bad_reference_mass_and_outside_domain_fail(props):
    uv = EquilibriumUV(props)
    n = normalized_source(props)
    with pytest.raises(ValueError,match="one kg"):
        uv.solve(1.,2*n,0.)
    with pytest.raises(ValueError,match="bracket"):
        uv.solve(1e6,n,-1e9)
