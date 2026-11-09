# Research workbench v1: completed implementation batch

9 November 2026 (continuation of the 8 November session).

## Delivered

A local, reusable **zero-dimensional equilibrium research workbench**. One command verifies the property/numerical layer, runs a source/mixing study, exports checked source contracts and generates a self-contained HTML report plus checksums. This is working research software, not the tanker application or a dispersion solver.

| Checkpoint | Delivered evidence |
|---|---|
| Reusable study API | Four source interpretations, configurable downstream temperature/humidity/pressure and mixing ratios; invalid inputs fail closed |
| Executed study | 4 sources × 3 humidities × 11 ratios = 132 conditional equilibrium states |
| Source-contract module | H00-H03 exports; 39 passed arithmetic/consistency checks per source; H02 liquid propane retained; H04 refused |
| Offline results report | 12 selectable paths, 24 SVG plots, full data table, assumptions and embedded provenance; no external assets |
| Reproducible bundle | Verification, study, handoffs, HTML and exact-byte SHA-256 manifest; existing runs protected |
| Automated checks | 136 passing Python tests; property gate passed; report JavaScript smoke check passed; dependency check passed |
| Continuous integration | Windows/Python 3.13 GitHub workflow passed on code commit 5b441d3; [run record](../../data/public/eec550-workbench-ci.json) |

[Open the offline report](../../data/public/eec550-research-bundle-v1/report.html) · [Study JSON](../../data/public/eec550-research-bundle-v1/study.json) · [Manifest](../../data/public/eec550-research-bundle-v1/manifest.json)

## Reproduce in one command

From the Avertiq repository root, using the existing environment:

~~~powershell
.\.venv\Scripts\python.exe -m avertiq_equilibrium bundle --output outputs/my-new-research-bundle
~~~

Open that directory's report.html in a browser. Use a fresh directory for each run. Failure before publication does not leave a partial final bundle. No new runtime dependencies were added.

For a smaller custom calculation without source-contract bundle:

~~~powershell
.\.venv\Scripts\python.exe -m avertiq_equilibrium study --sources H00 H02 --relative-humidities 0 0.99 --ratios 0 0.1 1 10 --output outputs/my-study.json
~~~

Optional arguments: --ambient-temperature in kelvin (273.16–300), --pressure in Pa (50000–200000), --ratios (strictly increasing unique values from 0–100). Source pressure and mixed-stream pressure match. A bundle uses 102500 Pa because its exported reference-source cases use that pressure; custom pressure studies use the study command. Bundle source exports always cover all four reference source interpretations, even when the study selects a subset.

## Findings

- H00/H01/H03 start with ice. Added moisture can first increase ice mass before warming removes it.
- In the dry and 50% RH downstream cases, all sampled source alternatives are gas-only at ratio 100; that is a calculated endpoint, not a general gas-only justification.
- At 99% RH downstream, liquid water remains at ratio 100. H00 ends near 282.49 K.
- H02 starts with liquid propane. Humid added air can create ice while that propane evaporates.
- Maximum absolute energy residual: **0.0000244 J/kg**. Maximum relative component residual: **1.39e-16**. These establish numerical accounting only.
- Transition records bracket changes between grid samples; they do not establish exact thresholds, monotonic behaviour or physical phase rates.

Ratio means added wet-air mass divided by the original selected source's total mass. It predicts no distance, time or real dilution rate. Momentum and kinetic-energy conversion are excluded from the mixing diagnostic.

## Important reference distinction

Source feed assumptions retain the original 283.05 K / RH99% definition; changing downstream humidity does not rebuild the source. H02 alone is the counterfactual source-water removal.

The new ambient-stream builder defines RH against the normalized liquid-water saturation curve adopted by the equilibrium closure. The older 11-point mixing module used the unnormalized NIST fit for ambient RH. Those historical results are unchanged; nonzero-ratio values need not exactly match the new study. Ratio zero reproduces the same source.

## Verification and practical limits

The complete local suite passed **136 tests**. It covers component/phase/enthalpy ledgers, humidity/source-basis separation, phase limits, malformed/nonfinite inputs, corrupted contracts, report injection protection, output preservation and bundle failure isolation. The generated bundle passed the 34-check property/numerical gate.

The Node smoke check executes the report's filtering script against a minimal DOM: all 12 scenario selections and restoration of all 132 states passed. It is not a browser layout/accessibility audit. Native-browser inspection timed out waiting for app approval; visual layout remains unverified.

~~~powershell
.\.venv\Scripts\python.exe -m pytest research/equilibrium -q
node research/equilibrium/tools/check_report.cjs outputs/my-new-research-bundle/report.html
.\.venv\Scripts\python.exe -m pip check
~~~

Native ThermoPack calls remain serial. Source contracts are a versioned research interface, not OpenFOAM input files. Enthalpy-reference mapping and phase-bearing transport are still unverified. The numerical tests do not establish historical source accuracy, equilibrium relaxation times, dispersion accuracy or operational safety.

## Next engineering checkpoint

Use these interfaces and regression data to select and test one phase-bearing transport implementation. The workbench now supplies repeatable source states, conserved-component ledgers, phase-change test cases and auditable outputs. A future solver must demonstrate conservative transport, buoyancy, changing phase partition and compatible enthalpy references before the EEC550 receptor comparison. HEM remains a conditional research approximation, not a validated atmospheric aerosol model.

No app, CFD, terrain-flow calculation, hazard map or historical Adoshi reconstruction was produced in this batch. The nine-case dispersion matrix remains held.

GitHub verification: [successful run 42552591781](https://github.com/guptavernit2-afk/Avertiq_/actions/runs/42552591781). This validates the code commit recorded in the linked result; documentation-only commits may follow.
