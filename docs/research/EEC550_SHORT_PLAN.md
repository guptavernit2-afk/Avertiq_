# EEC550: short comparison plan

8 November 2026. Planning only; no simulation or application code.

**Choose OpenFOAM Foundation 14 for our first local research comparison**, using its multicomponent-fluid solver with gravity and heat/species transport. It is free software; Windows setup uses WSL2. This is a research baseline, not yet the app's production engine.

1. **Prepare evidence:** EEC550's propane experiment, original weather, 30 concentration records and the documented downstream propane-air source. Keep Adoshi weather/terrain out of this experiment.
2. **Resolve source gaps:** confirm the EEC55-to-EEC550 mapping, source-plane position/height, coordinate convention, and concentration averaging window. Record assumptions if original evidence cannot resolve them.
3. **Prepare a flat-ground comparison:** use the cold mixed-gas inlet; initially exclude tanker discharge, fire, tunnels and valleys. SLAB's stock pure-chemical jet inlet does not directly match this source.
4. **Test numerical behaviour first:** conservation, species conversions, wind direction, clean-air boundary-layer stability, and sensitivity to mesh/time step/domain.
5. **Compare measurements:** predict at the actual sensor coordinates/heights and matching 150-second averaging window. Report errors, including zeros and discrepancies; do not tune until the map looks right.

**Not ready to run:** source geometry placement, averaging-window timing, atmospheric-boundary-layer treatment and numerical tolerances need review. EEC360 follows later; keep EEC560 out of tuning.

Next deliverable: a reviewed input sheet and agreed comparison criteria. No installation, simulation, accuracy claim or terrain-flow validation has happened.

[Full input and model plan](EEC550_COMPARISON_PLAN.md) · [Structured input record](../../data/public/eec550-input-plan.json)
