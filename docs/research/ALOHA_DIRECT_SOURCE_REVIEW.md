# Does ALOHA Direct Source match our propylene case?

14 November 2026. Documentation and CLI review only; actual propylene results remain pending.

**Partial match, not established thermodynamic equivalence.** Our four frozen cases prescribe gas already entering the atmosphere. The documented Direct Source input contract fits that limited task. We have not established that ALOHA 5.4.7 initializes that gas at our assumed 298.15 K, 101325 Pa and zero liquid fraction. Completing a run or reproducing its entered mass would not settle that question.

## What matches, and what is unresolved

| Item | Finding | Consequence for the frozen cases |
|---|---|---|
| Meaning of release rate | Installed 5.4.7 help defines gas entering air; Direct bypasses source-strength estimation | Baseline 0.1 kg/s is prescribed airborne gas, not tanker liquid loss or a calculated leak |
| Time treatment | Constant Direct rate, with continuous duration entered in minutes | 600 s maps to 10 min; 60 kg is input arithmetic only. Half/double-rate cases imply 30/120 kg |
| Source height | Installed help warns that Heavy Gas uses zero even when an entered elevated height appears in the summary | Our source height is already zero; this avoids that specific mismatch |
| Declared temperature and phase | Independent equilibrium screen supports pure propylene at the declared state | This tests physical plausibility of an assumption, not its implementation in ALOHA |
| Effective temperature, pressure, enthalpy, vapour fraction | No version-specific mass-Direct initialization rule established in the reviewed material | Remain null in the review report; do not substitute air temperature, a boiling temperature or a guessed flash fraction |
| Volume-mode storage fields | Installed help describes these as volume-to-mass conversion inputs | Switching units is not evidence that dispersion thermodynamics became controllable |
| Two-phase warning | Installed help says sparse Direct inputs may not distinguish gas from two-phase release | Neither a warning nor its absence establishes the emitted phase; Heavy Gas selection is not proof of aerosol treatment |

The installed help is identified by the SHA-256 records in [mapping evidence](../../research/dispersion/mapping-evidence.json), specifically `Direct_Source.htm`, `Direct_Source_Inputs.htm` and `Heavy_Gas_Dispersion.htm`. Its descriptions also support keeping tanker discharge, flashing and jet development outside this prescribed-source test. No property library is redistributed.

## Why the remaining source state matters

The [NOAA 5.4.4 technical documentation](https://response.restoration.noaa.gov/sites/default/files/ALOHA_Tech_Doc.pdf), sections 4.4 and 4.4.3 (printed pages 45 and 50–51), includes primary-source enthalpy and surface heat exchange in its heavy-gas formulation. It describes spatially and temporally constant ambient pressure and omission of initial jet momentum. It does not establish the numerical pressure or the 5.4.7 mass-Direct initialization temperature/phase in these passages. Treat it as a different-version explanation, not implementation proof. Equal prescribed masses can coexist with different thermodynamic assumptions; matching mass alone cannot close this gate.

## Could the documented interfaces resolve it without the desktop?

The official [technical resources page](https://response.restoration.noaa.gov/oil-and-chemical-spills/chemical-spills/resources/aloha-technical-resources.html) links [Communicating with ALOHA](https://response.restoration.noaa.gov/sites/default/files/Communicating_With_ALOHA.pdf) (March 2009). Sections 1–2 and appendices 1–2 describe mapping/threat-point exchange, change notifications and weather input. They do not establish a complete headless source-setup/run interface or an effective source-temperature/enthalpy query. No DLL was loaded or invoked during this investigation.

The separate [status/pass-file specification](https://response.restoration.noaa.gov/sites/default/files/ALOHA_Pass_Files.pdf) (April 2007, pages 1–3) describes zone drawing data and display text, plus receptor coordinates. It specifies no typed effective source-state record. A polygon or receptor coordinate therefore cannot establish source-state equivalence. These older specifications are leads for future evidence capture, not a tested 5.4.7 integration.

The scoped review found no version-specific initialization explanation that closes the gap. This is not a claim that no such documentation or source code exists anywhere. Generic chemical properties, a different chemical's reference run and copied storage labels are insufficient substitutes.

## Implemented and tested

[Source-treatment evidence](../../research/dispersion/source-treatment-evidence.json) records the findings and their source/section identifiers. The new check compares declared source semantics and normalized model entries: pure propylene, Direct/continuous mode, mass rate, duration and ground-level height, plus the declared gas/no-jet scope and independent equilibrium screen. It reports conflicts without changing the case. Matching this subset never grants source-state equivalence.

```powershell
python research/dispersion/propylene.py source-treatment-check --case baseline --output outputs/propylene/source-treatment-check.json
python -m unittest discover -s research/dispersion -p 'test_*.py' -v
```

Use a fresh output path. The [saved baseline review](../../data/public/dispersion-qualification-v1/propylene-source-treatment.json) contains no model results. Future observed-record inspections include the same separately labelled review. Frozen v1/v2 cases, observed templates and qualification gates remain unchanged.

Eight new synthetic tests cover all four cases, mismatched rate/time/height, unsupported source meanings, bounds and invalid numbers, separation of declared/effective state, report provenance and CLI overwrite protection. The package has 26 tests; these verify research tooling, not dispersion accuracy.

## Next decisive evidence

Retain ALOHA for exploratory reference work, with applicability pending. The precise question for version-specific documentation or a future maintainer enquiry is:

> For ALOHA 5.4.7, with pure propylene entered as a continuous Direct Source in kg/s at ground level, how are the primary-source temperature, pressure, enthalpy and vapour/aerosol fraction initialized for automatic dispersion selection and Heavy Gas calculations? Do volume-mode storage entries affect anything beyond conversion to mass, and what output or documentation demonstrates the initialization?

This is a prepared question, not a sent message. If the answer establishes compatibility, archive it with its version/scope and perform the four supervised runs, retaining warnings and output semantics. Other mapping gates (chemical identity/properties, ground temperature, roughness and output basis) still apply. If the answer establishes a mismatch, preserve this suite and review a new case version or model route with explicit source thermodynamics. Do not quietly change assumptions to accept a result.

No computer control, ALOHA execution, external contact, deployment or dashboard physics change was performed.
