"""UV inversion for the existing reduced equilibrium model.

Conserved variables use a one-kg composition: mol/kg, rho kg/m3, e J/kg.
The pressure/enthalpy closure is solved on U=H-PV and V=1/rho.
"""
import math
import numpy as np
from scipy.optimize import brentq

from .equilibrium import Equilibrium


class EquilibriumUV:
    """Domain-limited equilibrium EOS, not a general ThermoPack UV flash."""
    pressure_min_Pa = 50000.
    pressure_max_Pa = 200000.

    def __init__(self, properties):
        self.properties = properties
        self.equilibrium = Equilibrium(properties)

    def _inputs(self, density, composition, energy):
        if isinstance(density, (bool, str, bytes)) or isinstance(energy, (bool, str, bytes)):
            raise ValueError("Density and internal energy must be finite numbers")
        try:
            density, energy = float(density), float(energy)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("Density and internal energy must be finite numbers") from exc
        if not math.isfinite(density) or density <= 0 or not math.isfinite(energy):
            raise ValueError("Positive finite density and finite internal energy required")
        n = self.equilibrium.validate_feed(composition)
        if not math.isclose(float(n @ self.properties.mw), 1., rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError("Composition must be mol per kg, with exactly one kg reference mass")
        return density, n, energy

    def solve(self, density_kg_m3, component_mol_per_kg, internal_energy_J_kg,
              *, pressure_hint_Pa=102500.):
        rho, n, e = self._inputs(density_kg_m3, component_mol_per_kg, internal_energy_J_kg)
        if isinstance(pressure_hint_Pa, (bool, str, bytes)):
            raise ValueError("Pressure hint must be finite and inside the model domain")
        try:
            hint = float(pressure_hint_Pa)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("Pressure hint must be finite and inside the model domain") from exc
        lo, hi = self.pressure_min_Pa, self.pressure_max_Pa
        if not math.isfinite(hint) or not lo <= hint <= hi:
            raise ValueError("Pressure hint must be finite and inside the model domain")
        volume = 1./rho
        cache = {}
        def evaluate(pressure):
            pressure = float(pressure)
            if pressure not in cache:
                # Enthalpy target includes the unknown pressure-volume term.
                state = self.equilibrium.ph(pressure, n, e+pressure*volume)
                cache[pressure] = (state.volume_m3-volume, state)
            return cache[pressure]

        samples = {}
        def sample(pressure):
            if pressure in samples:
                return None
            try:
                residual, state = evaluate(pressure)
            except ValueError:
                # Some pressures require temperatures outside the reviewed bracket.
                # They are inadmissible search samples, never clipped states.
                samples[pressure] = None
                return None
            samples[pressure] = residual
            if abs(residual)/volume <= 1e-11:
                return state
            return None

        def bracket():
            valid = sorted((p, f) for p, f in samples.items() if f is not None)
            for (a, fa), (b, fb) in zip(valid, valid[1:]):
                if fa*fb < 0:
                    return a, b
            return None

        result = sample(hint)
        bounds = None
        if result is None:
            for factor in (0.02, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6):
                for pressure in (max(lo, hint*(1-factor)), min(hi, hint*(1+factor))):
                    result = sample(pressure)
                    if result is not None:
                        break
                if result is not None:
                    break
                bounds = bracket()
                if bounds:
                    break
        if result is None and not bounds:
            # A bounded fallback covers pressure states far from a caller's hint.
            for pressure in np.linspace(lo, hi, 25):
                result = sample(float(pressure))
                if result is not None:
                    break
                bounds = bracket()
                if bounds:
                    break
        if result is None:
            if not bounds:
                raise ValueError("UV state has no admissible pressure/temperature bracket")
            try:
                pressure = brentq(lambda p: evaluate(p)[0], *bounds, xtol=1e-7, rtol=1e-12)
                result = evaluate(pressure)[1]
            except (ValueError, RuntimeError) as exc:
                raise ValueError("UV state cannot be resolved inside the reviewed domain") from exc
        volume_residual = abs(result.volume_m3-volume)/volume
        energy_residual = abs(result.enthalpy_J-result.pressure_Pa*result.volume_m3-e)
        if (not math.isfinite(volume_residual) or volume_residual > 2e-8
                or not math.isfinite(energy_residual) or energy_residual > .01):
            raise RuntimeError("UV volume/internal-energy conservation gate failed")
        return result

    def _step(self, value, relative_step):
        if isinstance(relative_step, (bool, str, bytes)):
            raise ValueError("EOS derivative relative step must lie in [1e-6,1e-2]")
        try:
            valid = math.isfinite(relative_step) and 1e-6 <= relative_step <= 1e-2
        except TypeError as exc:
            raise ValueError("EOS derivative relative step must lie in [1e-6,1e-2]") from exc
        if not valid:
            raise ValueError("EOS derivative relative step must lie in [1e-6,1e-2]")
        return relative_step*100000.  # Fixed physical scale, invariant to energy-reference shifts.

    def sound_speed(self, density_kg_m3, component_mol_per_kg, internal_energy_J_kg,
                    *, state=None, relative_step=1e-4):
        rho, n, e = self._inputs(density_kg_m3, component_mol_per_kg, internal_energy_J_kg)
        de = self._step(e, relative_step)
        base = state if state is not None else self.solve(rho, n, e)
        hint = base.pressure_Pa
        drho = relative_step*rho
        pm = self.solve(rho-drho, n, e, pressure_hint_Pa=hint).pressure_Pa
        pp = self.solve(rho+drho, n, e, pressure_hint_Pa=hint).pressure_Pa
        dp_drho_e = (pp-pm)/(2*drho)
        pm = self.solve(rho, n, e-de, pressure_hint_Pa=hint).pressure_Pa
        pp = self.solve(rho, n, e+de, pressure_hint_Pa=hint).pressure_Pa
        dp_de_rho = (pp-pm)/(2*de)
        c2 = dp_drho_e+hint*dp_de_rho/rho**2
        if not math.isfinite(c2) or c2 <= 0:
            raise RuntimeError("Equilibrium sound-speed squared must be positive and finite")
        return math.sqrt(c2)

    def heat_capacity_cv(self, density_kg_m3, component_mol_per_kg, internal_energy_J_kg,
                         *, state=None, relative_step=1e-4):
        rho, n, e = self._inputs(density_kg_m3, component_mol_per_kg, internal_energy_J_kg)
        de = self._step(e, relative_step)
        base = state if state is not None else self.solve(rho, n, e)
        tm = self.solve(rho, n, e-de, pressure_hint_Pa=base.pressure_Pa).temperature_K
        tp = self.solve(rho, n, e+de, pressure_hint_Pa=base.pressure_Pa).temperature_K
        difference = tp-tm
        if abs(difference) <= 1e-10:
            return float("inf")  # A resolved constant-temperature latent plateau.
        if not math.isfinite(difference) or difference < 0:
            raise RuntimeError("Constant-volume caloric derivative must be positive")
        return 2*de/difference
