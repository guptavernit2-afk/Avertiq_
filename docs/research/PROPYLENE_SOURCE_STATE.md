# Propylene temperature and phase review

14 November 2026. CLI-only review; no ALOHA execution. Frozen v1/v2 cases and unrun observed templates are unchanged.

## What the evidence resolves

[NIST Chemistry WebBook: propene, CAS 115-07-1](https://webbook.nist.gov/cgi/cbook.cgi?ID=C115071&Mask=4) reports a normal boiling temperature of 225.6 +/- 0.6 K and a critical temperature of 365.2 +/- 0.8 K. At our declared 298.15 K and 101325 Pa, a pure equilibrium gas is consistent with those data. This is a thermodynamic inference about an assumed state. The listed Antoine fit covers only 165.81–225.98 K; we do not extrapolate it to 298.15 K or report a room-temperature saturation pressure. The reported spreads are screening exclusions, not certified uncertainty bounds.

The small attributed [property record](../../research/dispersion/propylene-state-evidence.json) and [baseline screen](../../data/public/dispersion-qualification-v1/propylene-source-state.json) make this inference reproducible. The checker accepts only pure propylene at exactly standard atmospheric pressure and strictly between the upper boiling and lower critical screening bands, with declared gas-only/no droplets. Other conditions remain unsupported; it does not classify them as liquid or estimate a flash fraction.

## Three questions that must stay separate

| Question | Current answer | Evidence needed to close it |
|---|---|---|
| Is the assumed warm gas state physically consistent? | Yes, within the bounded equilibrium screen | Recorded independent property source; now supplied |
| Does the real tanker emit that warm gas with no droplets? | Unknown | Cargo/composition, storage temperature/pressure, phase, inventory, opening geometry/location and applicable discharge/flash analysis; no measured values invented |
| Does ALOHA Direct Source use that state internally? | Not established by the reviewed documentation | Version-specific documented implementation or exposed source-state output with a defensible interpretation; the existence of an input field or warning alone is insufficient |

The installed Direct Source help describes a prescribed airborne gas rate, and warns that its limited inputs may not identify two-phase behaviour. A pressurized liquid release can require a different treatment from this already-gaseous source assumption. The independently plausible equilibrium state does not establish how an actual leak reaches that state, how quickly droplets evaporate, or which source enthalpy the engine uses.

The reviewed 5.4.7 mass-rate form has no independent source-temperature or pressure input. Volume-mode storage fields support volume-to-mass conversion; they do not prove a selectable cloud thermodynamic state. The 5.4.4 technical reference is a different version and does not close this installed-engine mapping from the passages reviewed. We therefore retain the full mapping gate. A future GUI run may expose useful output, but if it does not expose/establish the necessary source state, simply completing that run cannot close the gate.

## Implemented checks and remaining action

```powershell
python research/dispersion/propylene.py source-state-check --case baseline --output outputs/propylene/source-state-check.json
python -m unittest discover -s research/dispersion -p 'test_*.py' -v
```

`source_state.py` screens declarations only. The record inspector also includes this separately labelled screen alongside future observed records. Flags for actual phase/temperature, ALOHA internal verification, model execution, propylene qualification, field validation and dashboard integration remain false. No concentrations, plume dimensions, pressure correlation or tank-release predictions were added.

Eighteen tests now cover the preparation/evidence package. New tests check all four case assumptions, unsupported pressures/mixtures/droplets, boiling/critical boundaries and invalid numerics. Tests are synthetic code checks, not experimental validation.

The next decisive evidence is version-specific source-state documentation or suitable observed output. If neither establishes compatibility, keep ALOHA records as exploratory and revise the scenario or select a model with explicit, reviewable source thermodynamics before claiming a qualified result. Do not force acceptance by changing temperature, substituting propane, or interpreting an absent warning as proof of gas-only flow. No external contact or computer-control action has been taken.
