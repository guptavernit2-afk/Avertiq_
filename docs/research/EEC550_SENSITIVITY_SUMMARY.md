# EEC550 sensitivity study: short report

**Phase-review update, 8 November 2026:** the [humidity/phase review](EEC550_PHASE_REVIEW.md) does not accept the proposed gas-only baseline under the current inlet conditions. The sensitivity matrix is held pending source-state and phase/enthalpy reconciliation. Original assumptions below remain planning history, not runnable inputs.

8 November 2026. Plan only; no coding or simulations.

**Start with nine cases:** one baseline plus changes to:
- Inlet height: 0.195, 0.500 and 0.800 m.
- Source position: 5 m along the jet versus along measured wind.
- Wind: measured direction versus the documented ideal direction.
- Atmosphere: neutral versus estimated weak instability.
- Inlet turbulence: assumed 5%, 10% and 15% intensity.
- Ground: no heat exchange versus an assumed ambient-temperature surface.

Missing-input values are labelled assumptions, not measured limits. Keep documented source temperature, speed, composition and size fixed.

**Compare:** use the same sensors and concentration units. Report changes from baseline, errors against measurements, and results by sensor height. Test three 150-second model averaging windows without pretending we know the historical window.

**Check first:** conservation, mesh, time step, domain and stable atmosphere/plume. These checks add work beyond the nine physical cases.

Do not pick whichever assumption fits best. Keep EEC560 out of tuning. Two targeted interaction cases may follow if needed.

Before running, review humidity/phase behaviour, atmosphere/turbulence settings and numerical setup. The actual inlet elevation and observation timing remain unknown.

[Full plan](EEC550_SENSITIVITY_STUDY.md) · [Case record](../../data/public/eec550-sensitivity-plan.json)
