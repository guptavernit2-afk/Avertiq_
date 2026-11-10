# Working on Avertiq

## Current authorization

On 10 November 2026 the user explicitly authorized building the website dashboard and 3D map from the preview, with demo assessments clearly labelled until the physics is ready. This supersedes the earlier no-product-application boundary for the D-001 website only. Keep the research code and original SurakshaMitra prototype unchanged. Build incident inputs, geographic context, illustrative A/B revisions, synthetic observations and handover; do not enable unqualified hazard calculations or live dispatch. Site source synchronization/private preview publication is part of the website workflow. Preserve this repository's Git origin; any Sites source checkout must be isolated under outputs, not repoint this repository.

The user subsequently requested localhost instead of the hosted preview. Future development and previews are local-only unless the user explicitly requests publication. The user requested committing and pushing this first dashboard to the existing Avertiq repository, and asked to clarify the backend/workflow before extending the raw interface. The existing hosted copy is not authorization for further deployments.

Earlier research authorization covers equilibrium thermodynamics, conservative thermal flow and integration of heat/phase feedback with 2D buoyancy, and open atmospheric boundaries, EEC550 source/weather setup and grid/time-step studies, with parallel checkpoints, mathematical tests, commits and push. A new conservative compressible 2D formulation may replace the frozen-endpoint incompressible approximation for this stage; keep the old solver as a regression baseline. Distinguish bounded synthetic verification from EEC550 field validation. The newer D-001 website authorization above supersedes the earlier research-only boundary.

## Repository boundary

Use C:/Users/Vernit/OneDrive/Documents/Desktop/Avertiq_ explicitly as the working directory for every repository command. Never fall back to the chat's inherited SurakshaMitra directory. Before mutations, verify the Git top-level resolves to this folder and origin is https://github.com/guptavernit2-afk/Avertiq_.git. Stop on a mismatch. Do not modify or delete the original prototype as part of Avertiq work.

## Evidence and modelling

- Preserve the distinction between reported history, measurements, assumptions, and calculations.
- Never fabricate incident coordinates, tanker specifications, telemetry, or experimental results.
- Label all synthetic data; synthetic detector readings cannot validate physics.
- Record units, timestamps, reference systems, model versions, and source provenance.
- Compare models only with matched inputs, thresholds, averaging times, and applicable assumptions.
- Do not describe a visual terrain overlay as terrain-dependent dispersion.
- Do not label routes or places safe solely because they are outside a polygon.
- Do not import the original prototype's blast/fireball equations as established tanker-release models.

## Records

Update the relevant planning record with substantive decisions. Keep the roadmap concise, source status accurate, and commits scoped. Do not commit secrets, private shipment records, licensed PHAST materials, or large external datasets without checking authorization and redistribution terms.

## Verification

For documentation changes, check links, paths, CSV structure, scope consistency, and Git status. For the equilibrium research package, run its property checks and meaningful conservation/phase-limit tests. Numerical verification is not experimental validation. For flow changes, verify projection/divergence, hydrostatic balance, buoyancy controls, scalar/density conservation and timestep stability. For the website, verify fixture invalidation, immutable revisions, labelled exports, persistence and the core browser walkthrough; report map/network limitations honestly.
