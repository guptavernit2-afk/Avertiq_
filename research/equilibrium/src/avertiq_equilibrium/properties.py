"""ThermoPack pure-phase properties and independent reference correlations.

Gas mixing is ideal. Condensates are pure/immiscible. No reactions or phase slip.
All internal amounts are mol or mol/s; property enthalpies are J/mol.
"""
from functools import lru_cache
import math

import numpy as np
from scipy.optimize import brentq
from thermopack.cubic import cubic

COMPONENTS = ("C3", "N2", "O2", "AR", "H2O")
PROPANE, WATER = 0, 4
T_MIN, T_MAX = 180.0, 300.0


def scalar(value):
    array = np.asarray(value, dtype=float)
    if array.size != 1 or not np.isfinite(array).all():
        raise ValueError(f"Invalid scalar property: {value!r}")
    return float(array.reshape(-1)[0])


def propane_reference_pressure(t):
    """NIST low-temperature fit, valid 166.02--231.41 K, Pa."""
    if not 166.02 <= t <= 231.41:
        raise ValueError("Outside the selected NIST propane fit range")
    return 1e5 * 10 ** (4.01158 - 834.26 / (t - 22.763))


def water_reference_pressure(t):
    """NIST warm liquid-water fit, valid 273--303 K, Pa."""
    if not 273 <= t <= 303:
        raise ValueError("Outside the selected NIST liquid-water fit range")
    return 1e5 * 10 ** (5.40221 - 1838.675 / (t - 31.737))


def ice_reference_pressure(t):
    """IAPWS R14-08(2011), Eq. 6, Pa."""
    if not 50 <= t <= 273.16:
        raise ValueError("Outside IAPWS ice sublimation range")
    theta = t / 273.16
    terms = ((-21.2144006, .00333333333),
             (27.3203819, 1.20666667), (-6.10598130, 1.70333333))
    return 611.657 * math.exp(sum(a * theta**b for a, b in terms) / theta)


class NativePRProperties:
    """Native PR condensed phases plus ideal-gas ThermoPack calorics.

    Instances/native calls must remain serial: ThermoPack has active model state.
    """
    label = "ThermoPack-2.2.3 PR pure condensates / ideal gas"
    def __init__(self):
        self.eos = cubic(",".join(COMPONENTS), "PR")
        self.eos.init_solid("H2O")
        self.eos.set_tmin(T_MIN)
        self.r = float(self.eos.Rgas)
        self.mw = np.array([self.eos.compmoleweight(i + 1) * 1e-3
                            for i in range(len(COMPONENTS))])
        self._pure = np.eye(len(COMPONENTS))

    def validate(self, t, p):
        if not math.isfinite(t) or not T_MIN <= t <= T_MAX:
            raise ValueError(f"Temperature must be {T_MIN}--{T_MAX} K")
        if not math.isfinite(p) or not 5e4 <= p <= 2e5:
            raise ValueError("Equilibrium pressure must be 50000--200000 Pa")

    @lru_cache(maxsize=4096)
    def gas_h(self, t, i):
        self.eos.activate()
        return scalar(self.eos.idealenthalpysingle(t, i + 1))

    @lru_cache(maxsize=4096)
    def gas_g(self, t, p, i):
        self.eos.activate()
        s = scalar(self.eos.idealentropysingle(t, p, i + 1))
        return self.gas_h(t, i) - t*s

    @lru_cache(maxsize=4096)
    def condensed(self, t, p, i, phase):
        self.eos.activate()
        z = self._pure[i]
        if phase == "ice":
            if i != WATER:
                raise ValueError("Only water ice is supported")
            h = scalar(self.eos.solid_enthalpy(t, p, z))
            s = scalar(self.eos.solid_entropy(t, p, z))
            v = scalar(self.eos.solid_volume(t, p, z))
        elif phase == "liquid":
            h = scalar(self.eos.enthalpy(t, p, z, self.eos.LIQPH))
            s = scalar(self.eos.entropy(t, p, z, self.eos.LIQPH))
            v = scalar(self.eos.specific_volume(t, p, z, self.eos.LIQPH))
        else:
            raise ValueError(f"Unknown condensed phase {phase}")
        if v <= 0:
            raise ValueError("Nonpositive condensed molar volume")
        return h, h-t*s, v

    def saturation_fraction(self, t, p, i, phase):
        g = self.condensed(t, p, i, phase)[1]
        return math.exp((g-self.gas_g(t, p, i))/(self.r*t))

    @lru_cache(maxsize=32)
    def melting_temperature(self, p):
        def difference(t):
            return (self.condensed(t, p, WATER, "ice")[1]
                    - self.condensed(t, p, WATER, "liquid")[1])
        return brentq(difference, 265, 280, xtol=1e-9)


class Properties(NativePRProperties):
    """Reduced reference-saturation HEM, with ThermoPack caloric references.

    Propane: native NIST_MEOS liquid, ThermoPack ideal-gas calorics.
    Water: IAPWS ice / NIST liquid saturation Gibbs closure, using the
    same ThermoPack ideal-gas enthalpy reference in every water phase.
    Water condensed volumes use the native library; condensed Poynting
    corrections and gas fugacity departures are neglected explicitly.
    """
    label = ("ThermoPack C3 NIST_MEOS / ideal carrier gas; "
             "IAPWS-ice and NIST-water saturation Gibbs closure")

    def __init__(self):
        super().__init__()
        from thermopack.multiparameter import multiparam
        self.propane = multiparam("C3", "NIST_MEOS")
        self.propane.set_tmin(T_MIN)
        self.mw[PROPANE] = self.propane.compmoleweight(1)*1e-3
        self._water_scale = 611.657 / water_reference_pressure(273.16)

    @lru_cache(maxsize=4096)
    def gas_h(self, t, i):
        if i == PROPANE:
            self.propane.activate()
            return scalar(self.propane.idealenthalpysingle(t, 1))
        return super().gas_h(t, i)

    @lru_cache(maxsize=4096)
    def gas_g(self, t, p, i):
        if i == PROPANE:
            self.propane.activate()
            s = scalar(self.propane.idealentropysingle(t, p, 1))
            return self.gas_h(t, i)-t*s
        return super().gas_g(t, p, i)

    def water_saturation(self, t, phase):
        if phase == "ice":
            pressure = ice_reference_pressure(t)
            theta = t/273.16
            terms = ((-21.2144006, .00333333333),
                     (27.3203819, 1.20666667), (-6.10598130, 1.70333333))
            dlog_dt = sum(a*(b-1)*theta**(b-2) for a, b in terms)/273.16
        elif phase == "liquid":
            pressure = self._water_scale*water_reference_pressure(t)
            dlog_dt = math.log(10)*1838.675/(t-31.737)**2
        else:
            raise ValueError("Unknown water phase")
        return pressure, dlog_dt

    @lru_cache(maxsize=4096)
    def condensed(self, t, p, i, phase):
        if i == PROPANE:
            if phase != "liquid":
                raise ValueError("Only liquid propane is supported")
            self.propane.activate()
            h = scalar(self.propane.enthalpy(t, p, [1.], self.propane.LIQPH))
            s = scalar(self.propane.entropy(t, p, [1.], self.propane.LIQPH))
            v = scalar(self.propane.specific_volume(t, p, [1.], self.propane.LIQPH))
            return h, h-t*s, v
        if i != WATER:
            raise ValueError("Only propane and water may condense")
        psat, dlog_dt = self.water_saturation(t, phase)
        g = self.gas_g(t, p, WATER)+self.r*t*math.log(psat/p)
        # h = g - T*(dg/dT)_p. This preserves latent heat and one reference.
        h = self.gas_h(t, WATER)-self.r*t*t*dlog_dt
        v = super().condensed(t, p, WATER, phase)[2]
        return h, g, v

    @lru_cache(maxsize=32)
    def melting_temperature(self, p):
        # Low-pressure, zero-condensed-volume Gibbs approximation.
        # Normalize the liquid saturation curve at the IAPWS triple point.
        return 273.16

    def pure_propane_saturation(self, t):
        self.propane.activate()
        return scalar(self.propane.bubble_pressure(t, [1.])[0])
