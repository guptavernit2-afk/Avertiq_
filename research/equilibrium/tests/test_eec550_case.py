"""Input provenance, slab normalization and geometry/profile verification."""
from copy import deepcopy
import json
import math

import numpy as np
import pytest
from scipy.integrate import quad

from avertiq_equilibrium.eec550_case import (
    build_eec550_case, validate_eec550_case, neutral_wind_at_height,
    neutral_wind_cell_mean, source_face_overlaps)


@pytest.fixture
def case():
    return build_eec550_case()


def test_source_ledger_and_original_record_are_distinct(case):
    assert validate_eec550_case(case)["passed"]
    assert case["source"]["propane_mass_flow_kg_s"]==3.
    assert case["source"]["temperature_K"]==pytest.approx(204.26096230749)
    assert case["original_reported_equivalent_source"]["temperature_K"]==196.
    assert case["original_reported_equivalent_source"]["area_m2"]==.3042
    assert not case["faithful_reproduction"] and not case["sensor_comparison_ready"]
    assert json.loads(json.dumps(case,allow_nan=False))==case
    assert case["source"]["per_depth"]["propane_mass_kg_m_s"]!=3.


def test_wind_projection_preserves_magnitude_and_sign(case):
    a=case["atmosphere"]
    assert a["friction_velocity_m_s"]==pytest.approx(.15806032127083783)
    assert a["friction_velocity_m_s"]!=a["recorded_estimated_friction_velocity_m_s"]
    assert a["wind_projection_angle_deg"]==pytest.approx(-12.27)
    along=neutral_wind_at_height(6.,case)
    cross=a["omitted_crosswind_at_reference_m_s"]
    assert along==pytest.approx(2.66763856344884)
    assert cross<0
    assert math.hypot(along,cross)==pytest.approx(2.73)
    assert neutral_wind_at_height(0.,case)==0.
    assert neutral_wind_at_height(1.,case)<along<neutral_wind_at_height(8.,case)


def test_shifted_log_cell_average_against_quadrature(case):
    numerical=quad(lambda z:neutral_wind_at_height(z,case),0.,8.,epsabs=1e-10)[0]/8.
    assert neutral_wind_cell_mean(0.,8.,case)==pytest.approx(numerical,rel=1e-10)
    assert .5*(neutral_wind_cell_mean(0.,4.,case)+neutral_wind_cell_mean(4.,8.,case))==pytest.approx(numerical)


@pytest.mark.parametrize("cells",[4,8,16,64])
def test_exact_source_flux_and_potential_on_every_grid(case,cells):
    source=case["source"]
    overlap=source_face_overlaps(np.linspace(0.,8.,cells+1),case)
    lengths=overlap["overlap_lengths_m"]
    centres=overlap["overlap_centres_m"]
    assert sum(lengths)==pytest.approx(source["height_m"],abs=1e-14)
    assert sum(a*z for a,z in zip(lengths,centres))==pytest.approx(
        source["height_m"]*source["centre_height_m"],abs=1e-14)
    mass=source["density_kg_m3"]*source["speed_m_s"]*sum(lengths)
    assert mass==pytest.approx(source["total_mass_flow_kg_s"]/source["width_m"],rel=1e-12)
    for name,fraction in source["component_mass_fractions"].items():
        assert mass*fraction==pytest.approx(source["per_depth"]["component_mass_kg_m_s"][name],rel=1e-12)
    potential=source["density_kg_m3"]*source["speed_m_s"]*9.81*sum(
        a*z for a,z in zip(lengths,centres))
    assert potential==pytest.approx(source["per_depth"]["potential_energy_W_m"],rel=1e-12)
    assert all(0<=fraction<=1 for fraction in overlap["fractions"])


def test_partial_cell_intersection_not_rounded(case):
    overlap=source_face_overlaps([0.,.4,.6,1.],case)
    assert sum(overlap["overlap_lengths_m"])==pytest.approx(case["source"]["height_m"])
    assert overlap["overlap_lengths_m"][1]==pytest.approx(.2)
    assert overlap["overlap_centres_m"][1]==pytest.approx(.5)
    assert 0<overlap["fractions"][0]<1 and 0<overlap["fractions"][2]<1


def test_pressure_datum_effect_explicit(case):
    source=case["source"]
    assert 6.1<source["pressure_excess_at_centre_Pa"]<6.2
    assert source["hydrostatic_ambient_pressure_at_centre_Pa"]<source["pressure_Pa"]
    assert "datum assumption" in source["pressure_datum_note"]


@pytest.mark.parametrize("faces",[[0.],[0.,0.,8.],[8.,0.],[-1.,8.],[0.,float("nan")],[.4,8.],[0.,.6]])
def test_bad_or_truncated_patch_grids_refused(case,faces):
    with pytest.raises(ValueError):
        source_face_overlaps(faces,case)


@pytest.mark.parametrize("z",[-1.,float("nan"),float("inf"),True,"6"])
def test_bad_wind_height_refused(case,z):
    with pytest.raises(ValueError):
        neutral_wind_at_height(z,case)


@pytest.mark.parametrize("path,value",[
    (("source","temperature_K"),196.),
    (("source","total_mass_flow_kg_s"),20.),
    (("source","height_m"),.39),
    (("source","pressure_excess_at_centre_Pa"),0.),
    (("atmosphere","friction_velocity_m_s"),.190),
    (("atmosphere","temperature_K"),250.),
    (("atmosphere","relative_humidity"),float("nan")),
    (("atmosphere","omitted_crosswind_at_reference_m_s"),0.),
    (("domain","height_m"),.6),
])
def test_inconsistent_contract_refused(case,path,value):
    corrupt=deepcopy(case)
    corrupt[path[0]][path[1]]=value
    with pytest.raises(ValueError):
        validate_eec550_case(corrupt)


def test_no_mutable_singleton_or_invalid_readiness(case):
    changed=build_eec550_case()
    changed["source"]["component_mass_fractions"]["C3"]=0.
    assert build_eec550_case()["source"]["component_mass_fractions"]["C3"]>0
    changed=deepcopy(case)
    changed["faithful_reproduction"]=True
    with pytest.raises(ValueError):
        validate_eec550_case(changed)
