"""Actual open-boundary controls, conservative ledgers and refinement records."""
from copy import deepcopy
import json

import numpy as np
import pytest

from avertiq_equilibrium.atmospheric_checks import (
    audit_atmospheric_result, run_atmospheric_checks, run_refinement)


@pytest.fixture(scope="module")
def checked():
    return run_atmospheric_checks()


@pytest.fixture(scope="module")
def refinement():
    return run_refinement()


def test_controls_have_independent_budgets_and_strict_json(checked):
    decoded=json.loads(json.dumps(checked,allow_nan=False))
    assert decoded["passed"]
    assert len(decoded["checks"]) >= 100
    assert all(check["passed"] for check in decoded["checks"])
    assert decoded["background_normalized_drift"] < 1e-10
    assert all(audit["maximum_normalized_budget_residual"]<1e-10
               for audit in decoded["audits"].values())
    assert not decoded["case"]["faithful_reproduction"]
    assert not decoded["case"]["sensor_comparison_ready"]


def test_actual_outlet_pulse_and_backflow_fluxes(checked):
    controls=checked["controls"]
    outgoing=controls["outlet_tracer_pulse"]["atmospheric"]["per_side_accumulated_inward_integrals"]
    incoming=controls["outlet_backflow"]["atmospheric"]["per_side_accumulated_inward_integrals"]
    assert outgoing["right"][0] < 0.
    assert sum(incoming["right"][:5]) > 0.
    audit=checked["audits"]["outlet_tracer_pulse"]
    assert audit["final_integrals"][0] < audit["initial_integrals"][0]


def test_corrupt_raw_energy_is_rejected(checked):
    bad=deepcopy(checked["controls"]["source"])
    bad["final_conserved"][0][0][7] += 100.
    with pytest.raises(RuntimeError,match="budget"):
        audit_atmospheric_result(bad)


def test_nonfinite_raw_state_is_rejected(checked):
    bad=deepcopy(checked["controls"]["source"])
    bad["final_conserved"][0][0][0]=float("nan")
    with pytest.raises(RuntimeError,match="finite"):
        audit_atmospheric_result(bad)


def test_grid_study_is_matched_but_explicitly_unresolved(refinement):
    assert refinement["completed"]
    assert not refinement["field_comparison_ready"]
    assert refinement["spatial_convergence_status"]=="not_established_source_window_underresolved"
    grids=refinement["grid_cases"]
    assert [r["nx"] for r in grids]==[4,8,12]
    assert all(r["source_window_height_in_cells"] < 1 for r in grids)
    assert all(r["metrics"]["elapsed_s"]==pytest.approx(.001) for r in grids)
    expected=3./refinement["case"]["source"]["width_m"]*.001
    for row in grids:
        assert row["metrics"]["propane_inventory_kg_per_m_depth"]==pytest.approx(expected,rel=1e-10)
        assert row["metrics"]["maximum_normalized_budget_residual"] < 1e-10
    # Field metrics are reported, not judged accurate from conserved inventories.
    assert all(np.isfinite(row["metrics"]["maximum_total_propane_mass_fraction"])
               for row in grids)


def test_time_study_uses_distinct_nontrivial_steps_and_same_initial_state(refinement):
    study=refinement["time_step_refinement"]
    counts=study["step_count_sequence"]
    assert counts[0]>=2 and counts[0]<counts[1]<counts[2]
    assert study["cfl_sequence"]==[.2,.1,.05]
    runs=[refinement["grid_runs"][0]]+refinement["additional_time_step_runs"]
    for run in runs:
        np.testing.assert_array_equal(run["initial_conserved"],runs[0]["initial_conserved"])
        assert run["diagnostics"]["elapsed_s"]==pytest.approx(.001)
    assert len(study["pairwise_conservative_changes"])==2
    assert all(len(pair["mean_absolute_change_by_column"])==8
               for pair in study["pairwise_conservative_changes"])
    json.dumps(refinement,allow_nan=False)
