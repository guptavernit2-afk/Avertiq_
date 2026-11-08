"""Solid-aware TP equilibrium plus an enthalpy root and melting lever rule."""
from dataclasses import dataclass
import itertools
import math

import numpy as np
from scipy.optimize import brentq

from .properties import COMPONENTS, PROPANE, WATER, T_MIN, T_MAX


@dataclass
class State:
    temperature_K: float
    pressure_Pa: float
    gas_mol: np.ndarray
    propane_liquid_mol: float
    water_liquid_mol: float
    ice_mol: float
    enthalpy_J: float
    volume_m3: float
    mass_kg: float

    def component_amounts(self):
        totals = self.gas_mol.copy()
        totals[PROPANE] += self.propane_liquid_mol
        totals[WATER] += self.water_liquid_mol + self.ice_mol
        return totals

    def as_dict(self):
        ng = float(self.gas_mol.sum())
        return {
            "temperature_K": self.temperature_K, "pressure_Pa": self.pressure_Pa,
            "gas_mol": dict(zip(COMPONENTS, self.gas_mol.tolist())),
            "gas_mole_fractions": dict(zip(COMPONENTS, (self.gas_mol/ng).tolist())),
            "propane_liquid_mol": self.propane_liquid_mol,
            "water_liquid_mol": self.water_liquid_mol, "ice_mol": self.ice_mol,
            "enthalpy_J": self.enthalpy_J, "volume_m3": self.volume_m3,
            "mass_kg": self.mass_kg, "bulk_density_kg_m3": self.mass_kg/self.volume_m3,
        }


class Equilibrium:
    def __init__(self, properties):
        self.p = properties

    def validate_feed(self, totals):
        totals = np.asarray(totals, dtype=float)
        if totals.shape != (len(COMPONENTS),) or not np.isfinite(totals).all():
            raise ValueError("Feed must be five finite component amounts")
        if (totals < 0).any() or totals[[1, 2, 3]].sum() <= 0:
            raise ValueError("Nonnegative amounts and a positive carrier-gas amount required")
        return totals.copy()

    def tp(self, t, p, totals, *, water_phase=None, ice_fraction=None):
        """Amounts may be mol, or mol/s for a steady-flow energy calculation."""
        self.p.validate(t, p)
        totals = self.validate_feed(totals)
        if water_phase is None:
            water_phase = ("ice" if t < self.p.melting_temperature(p) else "liquid")
        if water_phase not in ("ice", "liquid"):
            raise ValueError("Water phase must be ice or liquid")
        if ice_fraction is not None:
            if not 0 <= ice_fraction <= 1:
                raise ValueError("Ice fraction must be between zero and one")
            if abs(t-self.p.melting_temperature(p)) > 1e-6:
                raise ValueError("Mixed ice/liquid fractions require the melting temperature")

        saturation = np.array([
            self.p.saturation_fraction(t, p, PROPANE, "liquid"),
            self.p.saturation_fraction(t, p, WATER, water_phase)])
        if not np.isfinite(saturation).all() or (saturation <= 0).any():
            raise ValueError("Invalid saturation thresholds")
        condensables = np.array([PROPANE, WATER])
        carrier = float(totals[[1, 2, 3]].sum())
        solution = None
        # Exhaust the four possible active condensate sets, retaining exact totals.
        for active_tuple in itertools.product((False, True), repeat=2):
            active = np.array(active_tuple)
            if any(active[j] and totals[i] == 0 for j, i in enumerate(condensables)):
                continue
            denominator = 1 - saturation[active].sum()
            if denominator <= 0:
                continue
            ng = (carrier + totals[condensables[~active]].sum()) / denominator
            gas_c = np.where(active, saturation*ng, totals[condensables])
            condensed = totals[condensables] - gas_c
            if (condensed < 0).any():
                continue
            if any(not active[j] and gas_c[j]/ng > saturation[j]*(1+1e-10)
                   for j in range(2)):
                continue
            solution = (gas_c, condensed)
            break
        if solution is None:
            raise RuntimeError("No admissible equilibrium phase set")

        gas_c, cond = solution
        gas = totals.copy()
        gas[condensables] = gas_c
        wi = float(cond[1]) if water_phase == "ice" else 0.0
        wl = float(cond[1]) if water_phase == "liquid" else 0.0
        if ice_fraction is not None:
            wi = float(cond[1])*ice_fraction
            wl = float(cond[1])*(1-ice_fraction)
        pl = float(cond[0])
        h = sum(gas[i]*self.p.gas_h(t, i) for i in range(len(COMPONENTS)))
        volume = gas.sum()*self.p.r*t/p
        for i, phase, amount in ((PROPANE, "liquid", pl),
                                  (WATER, "liquid", wl), (WATER, "ice", wi)):
            if amount > 0:
                hp, _, vp = self.p.condensed(t, p, i, phase)
                h += amount*hp
                volume += amount*vp
        return State(float(t), float(p), gas, pl, wl, wi, float(h),
                     float(volume), float(np.dot(totals, self.p.mw)))

    def ph(self, p, totals, target_J, *, lower_K=T_MIN, upper_K=T_MAX):
        totals = self.validate_feed(totals)
        if not math.isfinite(target_J) or not T_MIN <= lower_K < upper_K <= T_MAX:
            raise ValueError("Invalid energy target or temperature bracket")
        self.p.validate(lower_K, p)
        tm = self.p.melting_temperature(p)
        ice = self.tp(tm, p, totals, water_phase="ice")
        liquid = self.tp(tm, p, totals, water_phase="liquid")
        span = liquid.enthalpy_J - ice.enthalpy_J
        if span < -1e-5:
            raise RuntimeError("Ice/liquid latent heat has the wrong sign")
        if lower_K <= tm <= upper_K and span > 1e-6:
            if ice.enthalpy_J <= target_J <= liquid.enthalpy_J:
                fraction = (liquid.enthalpy_J-target_J)/span
                state = self.tp(tm, p, totals, water_phase="ice",
                                ice_fraction=float(fraction))
                self.check_energy(state, target_J)
                return state
        # Split at the melting plateau so a jump cannot masquerade as a root.
        if target_J <= ice.enthalpy_J:
            a, b, phase = lower_K, min(tm, upper_K), "ice"
        else:
            a, b, phase = max(tm, lower_K), upper_K, "liquid"
        if a > b:
            raise ValueError("Enthalpy outside the requested bracket")
        def residual(t):
            return self.tp(t, p, totals, water_phase=phase).enthalpy_J-target_J
        fa, fb = residual(a), residual(b)
        if fa == 0:
            t = a
        elif fb == 0:
            t = b
        elif fa*fb > 0:
            raise ValueError("Enthalpy outside the requested temperature bracket")
        else:
            t = brentq(residual, a, b, xtol=1e-8, rtol=1e-12)
        state = self.tp(t, p, totals, water_phase=phase)
        self.check_energy(state, target_J)
        return state

    @staticmethod
    def check_energy(state, target_J):
        if abs(state.enthalpy_J-target_J)/state.mass_kg > 1.0:
            raise RuntimeError("Enthalpy residual exceeds 1 J/kg")

    def diagnostics(self, state, feed, target_J=None):
        feed = self.validate_feed(feed)
        delta = state.component_amounts()-feed
        relative = [abs(delta[i])/feed[i] if feed[i] > 0 else abs(delta[i])
                    for i in range(len(feed))]
        ratios = {}
        gas_total = state.gas_mol.sum()
        water_phases = []
        if state.ice_mol > 0: water_phases.append("ice")
        if state.water_liquid_mol > 0: water_phases.append("liquid")
        if not water_phases:
            water_phases = ["ice" if state.temperature_K <
                            self.p.melting_temperature(state.pressure_Pa) else "liquid"]
        for i, phase in [(PROPANE, "liquid")]+[(WATER, v) for v in water_phases]:
            y = state.gas_mol[i]/gas_total
            sat = self.p.saturation_fraction(
                state.temperature_K, state.pressure_Pa, i, phase)
            ratios[COMPONENTS[i]+"_"+phase] = float(y/sat)
        return {
            "component_residual_mol": dict(zip(COMPONENTS, delta.tolist())),
            "maximum_component_relative_residual": float(max(relative)),
            "gas_saturation_ratios": ratios,
            "energy_residual_J_kg": None if target_J is None else
                float((state.enthalpy_J-target_J)/state.mass_kg),
        }
