# EEC550: short research update

**Phase-review update, 8 November 2026:** the [humidity/phase review](EEC550_PHASE_REVIEW.md) does not accept the proposed gas-only baseline under the current inlet conditions. The sensitivity matrix is held pending source-state and phase/enthalpy reconciliation. Original assumptions below remain planning history, not runnable inputs.

8 November 2026. Research saved; no coding or simulations.

**We resolved how to handle the gaps, but two historical details are still missing.**

1. **Placement:** the experimental axes are established. The original nozzle is 0.5 m high, but the downstream mixed-gas inlet height is not documented. We recorded an assumed placement and alternatives; none is labelled measured.
2. **Timing:** EEC55 had a fence removed during a longer release. The 150-second SMEDIS mean must not automatically be treated as a fresh 150-second leak. Our proposed first comparison uses a developed, unfenced plume, then a 150-second model averaging window.
3. **Weather:** retain the corrected experimental wind. Use an explicitly simplified neutral baseline; test the estimated weak instability separately instead of forcing inconsistent weather inputs together.

**Still needed:** the actual downstream inlet elevation and exact observation-window timing, plus thermal/turbulence setup review. A public link to the original REDIPHEM archive currently returns “Download not available.”

OpenFOAM Foundation 14 remains the planned research platform. A faithful reproduction is **not ready to run**. The next step is recovering those records or explicitly agreeing to a conditional sensitivity study.

[Findings and evidence](EEC550_INPUT_RESOLUTION.md) · [Full comparison plan](EEC550_COMPARISON_PLAN.md) · [Structured input record](../../data/public/eec550-input-plan.json)

## Sensitivity planning follow-up

The user has now requested a clearly labelled conditional sensitivity-study plan. See the [short study report](EEC550_SENSITIVITY_SUMMARY.md): nine core physical cases, three model-time averaging windows, separate numerical checks and no fitting. This authorizes planning only. The unresolved historical inputs above remain unknown; no cases have been run.
