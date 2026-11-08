# Standalone equilibrium implementation and verification

8 November 2026. Scope: conditional 0D thermodynamics only. No app, OpenFOAM installation, CFD or field validation.

## Outcome

Implemented the [standalone research package](../../research/equilibrium/README.md), installed ThermoPack 2.2.3 in an isolated local environment, and executed H00–H04.

**38 tests passed; all 34 CLI property/numerical checkpoints passed.** Dependency consistency also passed. These checks verify the specified reduced calculation; they do not establish experimental accuracy or validate the historical source.

## Property decision made before case results

The initial native Peng–Robinson-water/ice plus ideal-gas setup predicted 0.04981 Pa ice vapour pressure at 196 K, versus IAPWS 0.08693 Pa: about 43% low. It was rejected. A water-association probe also missed the reference substantially. The installed ThermoPack multiparameter interface does not provide H2O NIST_MEOS, so that was not adopted.

The implemented reduced model uses:
- ThermoPack C3 NIST_MEOS liquid and ideal-gas calorics; ideal N2/O2/Ar/water-vapour calorics.
- IAPWS ice and NIST liquid-water saturation relations, with condensed Gibbs energies on the same ThermoPack gas reference.
- Analytically derived phase enthalpies from H=G-T*dG/dT. Latent heat is included once.
- Native condensed volumes for the density diagnostic. The rejected native water Gibbs/enthalpy closure is not used for equilibrium energy.
- A normalized liquid-water curve meeting ice at 273.16 K, with a lever rule for partial melting.

The water closure is an explicit revision of the earlier property-library plan. It is not a claim that calling ThermoPack's ordinary two-phase PH interface includes ice. No condensation rate, particle dynamics or ice kinetics is calculated.

## Numerical method

At fixed pressure and temperature, enumerate all four active/inactive combinations of propane and water condensation. Carrier gases remain gaseous. Solve gas amounts from conservation and saturation constraints; reject negative phase amounts and supersaturated inactive phases.

For PH calculations, solve the total phase enthalpy target with a bracketed root. Split the temperature domain at melting; when the target lies within the melting latent-heat interval, solve the ice/liquid fraction at constant temperature rather than accepting a false root across a jump.

The code domain is 180–300 K and 50–200 kPa for equilibrium, with nonzero carrier gas. The EEC550 liquid-feed enthalpy uses its separate upstream pressure. Condensates are pure and immiscible; gas fugacity departures, dissolved gas, phase slip and finite-rate effects are omitted. Water pressure corrections are neglected; melting at 273.16 K is a low-pressure approximation, not the exact one-atmosphere freezing curve.

## What was checked

- Pure C3 saturation versus independent NIST fit points at 196/200/230 K: within the 0.5% screening tolerance.
- Reduced ideal-gas C3 saturation threshold: within a separate 5% screen, exposing the ideal-gas approximation.
- Fixed IAPWS ice reference pressures, including 230 K = 8.94735 Pa and the triple point.
- Water fusion enthalpy: approximately 334.5 kJ/kg versus the comparison value 333.4 kJ/kg; within the proposed 5 kJ/kg screen.
- Independent finite differences of Gibbs energy reproduce phase enthalpy.
- Cold propane-liquid/ice coexistence, warm liquid-water and all-gas limits, dry limit and phase appearance.
- PH temperature recovery, component/energy conservation over scaled feeds, and 25 deterministic randomized TP feeds.
- Ice/liquid melting fractions, reference-enthalpy shifts, invalid inputs, out-of-bracket energies and refused output overwrite.
- Failed verification blocks CLI case execution.

Internal conservation targets: relative component residual <=1e-8 and energy residual <=1 J/kg. H00–H03 returned component residuals zero at stored precision and energy residual magnitudes below 1e-6 J/kg. These small numerical errors are not estimates of physical modelling uncertainty.

## Conditional results

All values below depend on the declared feed/source assumptions; displayed precision is reduced deliberately.

| Case | Temperature K | Gas propane mol% | Liquid propane kg/s | Ice kg/s | Implied window area m2 |
|---|---:|---:|---:|---:|---:|
| H00: wet total-feed interpretation | 204.3 | 20.19 | 0 | 0.05769 | 0.3085 |
| H01: dry-feed concentration basis, moist air | 205.1 | 20.00 | 0 | 0.05838 | 0.3126 |
| H02: counterfactual dry control | 199.4 | 18.82 | 0.2515 | 0 | 0.2960 |
| H03: upstream gauge-pressure interpretation | 204.3 | 20.19 | 0 | 0.05769 | 0.3085 |
| H04: imposed 196 K TP audit | 196.0 | 15.24 | 0.8672 | 0.05771 | 0.2788 |

H00–H03 conserve the assumed incoming thermal and kinetic energy against outgoing phase enthalpy and prescribed velocity. The H00 gas result is compatible with no liquid propane in this reduced calculation, but water ice remains.

H04 fixes temperature instead of enforcing the PH energy target. It requires approximately **496 kW of additional heat removal** relative to the assumed adiabatic feed (external heat sign is negative into the control volume). That is an implied discrepancy, not evidence of real heat loss. Its nonzero adiabatic residual is intentional and explicitly labelled in the result record.

The reported 196 K / 20 mol% all-gas inlet is not recovered. Do not overwrite the original equivalent-source note with H00 or apply its temperature to the original rectangle while forcing every other field unchanged.

Dry-air fractions are assumed normalized N2/O2/Ar with CO2 omitted. Executed molar masses come from the installed backend; previous hand ledgers used rounded molecular weights. The nominal propane mass is preserved at exactly 3 kg/s. This small convention change is recorded in outputs.

## Reproducibility and records

- [Committed verification record](../../data/public/eec550-equilibrium-verification.json)
- [Committed conditional case results](../../data/public/eec550-equilibrium-results.json)
- [Run instructions and dependency lock](../../research/equilibrium/README.md)
- Local complete run directory: outputs/thermodynamics/2026-11-08-equilibrium-v2/ (ignored)

Commands executed from Avertiq:
```text
.venv/Scripts/python.exe -m pytest research/equilibrium -q
.venv/Scripts/python.exe -m avertiq_equilibrium verify --output outputs/thermodynamics/2026-11-08-equilibrium-v2/verification.json
.venv/Scripts/python.exe -m avertiq_equilibrium cases --output outputs/thermodynamics/2026-11-08-equilibrium-v2/cases.json
.venv/Scripts/python.exe -m pip check
```

Python 3.13.6; ThermoPack 2.2.3; NumPy 2.5.4; SciPy 1.18.1. Reports include native DLL SHA-256, package versions and LF-normalized source hashes. The installed PyPI wheel is not claimed to equal the earlier research snapshot of the upstream main branch. Lock file includes test dependencies.

## What this permits next

The calculation is ready for scientific review and further source-interpretation studies. It does not authorize or establish a suitable CFD configuration. The nine-case dispersion matrix remains held: it needs a reviewed phase-bearing source representation, inlet placement, averaging policy and atmospheric/numerical setup.

The short residence-time scale, unknown source basis and possible nonequilibrium phase behaviour still limit applicability. H00 is a conditional model result, not the historical truth. This implementation does not support operational clearance, tanker discharge validation or terrain-flow predictions.

References: [NIST propane](https://webbook.nist.gov/cgi/cbook.cgi?ID=C74986&Mask=FEF&Plot=on&Type=ANTOINE&Units=SI), [NIST water](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Plot=on&Type=ANTOINE), [IAPWS release](https://iapws.org/technical-guidance/release/MeltSub), [ThermoPack 2.2 methods](https://thermotools.github.io/thermopack/v2.2.0/thermo_methods.html).

[Short report](EEC550_EQUILIBRIUM_SUMMARY.md)
