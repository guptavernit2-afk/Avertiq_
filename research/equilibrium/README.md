# Standalone source equilibrium research

This package implements a **reduced, zero-dimensional equilibrium model** for conditional EEC550 source studies. It contains no app, map, CFD, release-rate model or operational hazard calculation.

Tested on Windows x64, Python 3.13.6, ThermoPack 2.2.3. Dependencies are isolated in the repository's ignored .venv directory. Numerical results and scientific limitations are in [the verification report](../../docs/research/EEC550_EQUILIBRIUM_VERIFICATION.md).

## Reproduce from the Avertiq repository root

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r research/equilibrium/requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install -e research/equilibrium
.\.venv\Scripts\python.exe -m pytest research/equilibrium -q
.\.venv\Scripts\python.exe -m avertiq_equilibrium verify --output outputs/thermodynamics/my-run/verification.json
.\.venv\Scripts\python.exe -m avertiq_equilibrium cases --output outputs/thermodynamics/my-run/cases.json
```

For an existing environment, omit venv creation. Use a fresh output directory: the CLI refuses to overwrite results. Case execution first runs the verification gate. Runtime pins include test dependencies; portability to other Python/platform combinations is not yet tested.

## Physics implemented

- Ideal-gas mixing of propane, N2, O2, Ar and water vapour.
- Pure immiscible liquid propane, pure liquid water and water ice.
- Exhaustive active-condensate sets enforce component conservation and saturation/complementarity.
- A pressure/enthalpy outer solve conserves energy; a lever rule handles the ice/liquid melting plateau.
- No reaction, gas nonideality, mutual condensate solubility, phase slip, deposition or finite-rate phase kinetics.
- Equilibrium domain: 180–300 K, 50–200 kPa; a positive carrier-gas amount is required. EEC550 liquid feed enthalpy is separately evaluated at 286.45 K and its stated pressure branch.

ThermoPack supplies C3 NIST_MEOS liquid/ideal-gas calorics, carrier/water ideal-gas calorics and condensed volumes. The initial PR/ice saturation combination failed the water property screen and is retained only as a rejected audit candidate.

**Water revision:** IAPWS ice-sublimation and NIST liquid-water saturation curves define pure condensed Gibbs energies against the same ThermoPack water-gas reference:
G_c = G_g,ideal + R*T*ln(p_sat/p),
H_c = H_g,ideal - R*T^2*dln(p_sat)/dT.

The derivative is analytic. Latent heat is already in H_c; it is never added again. Normalize the liquid-water curve to the IAPWS triple-point pressure at 273.16 K so liquid/ice Gibbs energies meet. This approximates melting as pressure-independent at 273.16 K, neglecting condensed-phase pressure corrections. Native ice volume is used for density, not the rejected PR/ice enthalpy closure. These are explicit low-pressure approximations.

The pure C3 EOS pressure check uses a 0.5% tolerance against NIST; the ideal-gas reduced saturation threshold uses a separate 5% screening tolerance to expose its fugacity approximation. Neither bounds the total model's physical error.

## Units and outputs

Generic TP/PH APIs use mol and J; the EEC550 driver interprets amounts as mol/s and enthalpy totals as W. Serialized case fields explicitly use mol/s, kg/s, W and m3/s. Diagnostics report component residuals and energy residual in J/kg. Each report records package versions, native-library hash and Python source hashes.

H00–H03 conserve the assumed steady-feed energy. H04 imposes 196 K and reports the additional external heat required; its nonzero energy mismatch is the audit result, not a failed PH solve.

Dry-air composition is an assumed N2/O2/Ar mixture, normalized after omitting CO2. Molar masses come from the installed ThermoPack backend, so executed feeds differ slightly from earlier hand ledgers that used rounded molecular weights. The nominal propane mass rate remains exactly 3 kg/s.

## Evidence and limitations

Reference fits and units originate in the tracked [phase-screen record](../../data/public/eec550-phase-screen.json). Property tests check fixed published points and the thermodynamic identity H=G-T*dG/dT, not just solver self-consistency. Tests also cover phase limits, melting, scaling, reference shifts, invalid inputs and failure handling.

Passing numerical and property checks **does not validate EEC550 dispersion or identify the historical source**. The same limitations apply to the committed small result records. Original inlet position, observation window and source-basis uncertainties persist. No results from this package should be used for responder clearance or tanker consequence predictions.

ThermoPack is an external dependency, not vendored source. See its [versioned documentation](https://thermotools.github.io/thermopack/v2.2.0/thermo_methods.html) and [PyPI release](https://pypi.org/project/thermopack/2.2.3/) for upstream terms and citation guidance.

## H00/ambient mixing diagnostic

The verification-gated mixing command adds humid ambient air to H00 at 11 prescribed wet-air/source mass ratios and solves constant-pressure thermal-enthalpy equilibrium. It predicts phase/composition changes, not distance, time or momentum. Kinetic-energy conversion is excluded explicitly.

~~~powershell
.\.venv\Scripts\python.exe -m avertiq_equilibrium mixing --output outputs/thermodynamics/my-new-mixing-run/mixing.json
~~~

Use a fresh output path. [Executed milestone and limitations](../../docs/research/EEC550_MIXING_MILESTONE.md). The expanded research suite has 51 passing tests. Earlier case outputs retain their original source hashes; new mixing output includes the extended CLI/module snapshot.
