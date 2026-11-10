# Adoshi demo scope

This document defines the **first walkthrough**, not the whole project. The 10 November 2026 [research scope](research/CHEMICAL_AND_STORAGE_SCOPE.md) additionally covers LPG/CNG, storage and light/heavy release behaviour, with separately qualified dispersion/fire/blast/terrain calculations. These remain later calculation milestones; they are not implemented by the initial map demo.

## Purpose

Demonstrate how an emergency coordinator and a hazmat specialist can assemble incomplete information, compare documented release scenarios, inspect geographic context, and maintain a shared incident record.

This is a training and evaluation demo inspired by the February 2026 Adoshi incident. Historical gas movement is unknown.

## Included

- One stationary propylene tanker and one incident at a time.
- An approximate incident location until independently verified.
- Public roads and terrain context, with coverage and limitations recorded.
- Reported incident background separated from hypothetical tank/release inputs.
- One complete first walkthrough, D-001, with two revisions after a simulated weather update. The three research scenarios remain available for later assessment work.
- Clearly labelled illustrative assessment fixtures for the first walkthrough. Physics-generated flammable-cloud outputs follow selection and comparison of a suitable calculation workflow.
- Distinct layers for model envelopes, field observations, and operational annotations.
- Synthetic observations and response updates for demonstrating the workflow.
- Versioned assessments and a short handover report.

## Deferred

- A moving release source, national fleet platform, and actual SCADA/telematics connections.
- Custom fire, BLEVE, and explosion models.
- Tunnel-interior dispersion and terrain-dependent concentration predictions.
- Automatic dispatch, evacuation orders, or road-reopening decisions.
- Claims of exact Adoshi reconstruction or operational validation.

## Acceptance

A reviewer can identify the origin and status of every important input, reproduce each supported assessment, distinguish synthetic observations from predictions, and explain the model's limitations. Earlier assessments remain available when conditions change.

Displaying a 3D landscape does not change the physics. Geographic context must never imply that terrain effects were calculated.

The five screen sketches and walkthrough acceptance criteria are defined in [the product brief](PRODUCT_BRIEF.md).
