"""Traceable conditional EEC550 2D slab inputs; not a field reproduction."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

COMPONENTS = ("C3", "N2", "O2", "AR", "H2O")
REPOSITORY = Path(__file__).resolve().parents[4]


def _number(value, name, *, minimum=None, positive=False):
    if isinstance(value, (bool, str, bytes)):
        raise ValueError(name+" must be numeric")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name+" must be finite numeric") from exc
    if not math.isfinite(value) or (positive and value <= 0) or (minimum is not None and value < minimum):
        raise ValueError("Invalid "+name)
    return value


def _record(relative):
    path = REPOSITORY/relative
    text = path.read_text(encoding="utf-8")
    return json.loads(text), {"path":relative, "sha256_normalized_UTF8_LF":hashlib.sha256(text.encode("utf-8")).hexdigest()}


def build_eec550_case():
    """Build a fresh versioned configuration from tracked first-party records."""
    handoff, handoff_lineage = _record("data/public/eec550-dispersion-handoff.json")
    study, study_lineage = _record("data/public/eec550-research-bundle-v1/study.json")
    ambient = next(p["ambient"] for p in study["paths"]
                   if p["source_id"]=="H00" and p["ambient"]["relative_humidity"]==.99)
    b = handoff["boundary"]
    masses = deepcopy(b["total_component_mass_kg_s"])
    mass = b["total_mass_kg_s"]
    width, height = b["window_width_m"], b["window_height_m"]
    speed = b["speed_m_s"]
    h = b["thermal_enthalpy_J_kg"]
    heading, wind_from = 30., 197.73
    downwind = (wind_from+180.)%360.
    delta = (downwind-heading+180.)%360.-180.
    wind_reference, reference_height, roughness, kappa = 2.73, 6., .006, .4
    friction = kappa*wind_reference/math.log((reference_height+roughness)/roughness)
    ground_pressure, gravity = 102500., 9.81
    rho_ambient = ambient["bulk_density_kg_m3"]
    source_centre = b["window_centre_xyz_m"][2]
    hydro_pressure = ground_pressure*math.exp(-gravity*rho_ambient/ground_pressure*source_centre)
    per_depth_components = {k:v/width for k,v in masses.items()}
    case = {
        "schema_version":1,
        "case_id":"EEC550-H00-2D-OPEN-v1",
        "status":"conditional_2D_source_weather_smoke_setup_not_field_validation",
        "faithful_reproduction":False,
        "sensor_comparison_ready":False,
        "lineage":{"source_handoff":handoff_lineage,"ambient_property_record":study_lineage,
                   "original_input_plan":"data/public/eec550-input-plan.json"},
        "source":{
            "basis":"conditional H00 reduced-equilibrium result",
            "temperature_K":b["temperature_K"],"pressure_Pa":b["pressure_Pa"],
            "density_kg_m3":b["bulk_density_kg_m3"],
            "thermal_enthalpy_J_kg":h,
            "speed_m_s":speed,"velocity_z_m_s":0.,
            "centre_height_m":source_centre,"height_m":height,"width_m":width,
            "area_m2":b["window_area_m2"],
            "total_mass_flow_kg_s":mass,"propane_mass_flow_kg_s":masses["C3"],
            "total_component_mass_kg_s":masses,
            "component_mass_fractions":{k:v/mass for k,v in masses.items()},
            "phase_mass_fractions":{"gas":b["gas_mass_kg_s"]/mass,
                                   "water_ice":b["ice_mass_kg_s"]/mass,
                                   "water_liquid":b["liquid_water_mass_kg_s"]/mass,
                                   "propane_liquid":b["liquid_propane_mass_kg_s"]/mass},
            "per_depth":{
                "total_mass_kg_m_s":mass/width,"propane_mass_kg_m_s":masses["C3"]/width,
                "component_mass_kg_m_s":per_depth_components,
                "advective_momentum_N_m":mass/width*speed,
                "pressure_traction_N_m":b["pressure_Pa"]*height,
                "full_normal_momentum_N_m":mass/width*speed+b["pressure_Pa"]*height,
                "enthalpy_plus_kinetic_W_m":mass/width*(h+.5*speed*speed),
                "potential_energy_W_m":mass/width*gravity*source_centre,
            },
            "hydrostatic_ambient_pressure_at_centre_Pa":hydro_pressure,
            "pressure_excess_at_centre_Pa":b["pressure_Pa"]-hydro_pressure,
            "pressure_datum_note":"H00 stays at 102500 Pa; assigning ambient 102500 Pa at ground creates a small positive source pressure excess. This is an explicit datum assumption, not measured thrust.",
            "geometry_evidence":"Centre height 0.5 m, top-hat profile and aspect ratio are assumptions; area/width/height are H00 flow-consistent calculations."
        },
        "atmosphere":{
            "temperature_K":283.05,"relative_humidity":.99,
            "ground_pressure_Pa":ground_pressure,
            "pressure_datum_height_m":0.,
            "pressure_datum_evidence":"Ground datum assumed; original database pressure measurement height is unknown.",
            "density_at_ground_kg_m3":rho_ambient,
            "humidity_definition":"Relative to the adopted normalized liquid-water saturation closure; original source-feed water convention remains unchanged.",
            "wind_reference_speed_m_s":wind_reference,
            "wind_reference_height_m":reference_height,
            "wind_from_deg_magnetic":wind_from,"downwind_deg_magnetic":downwind,
            "wind_direction_datum_note":"Raw selected wind-from 197.73 degrees is treated in the common local magnetic-north frame for this projection. Its independent compass datum was not recovered; no declination correction is applied.",
            "roughness_length_m":roughness,"kappa":kappa,
            "friction_velocity_m_s":friction,
            "recorded_estimated_friction_velocity_m_s":.190,
            "wind_profile":"shifted neutral log: U(z)=ustar/kappa*ln((z+z0)/z0)",
            "stability":"assumed neutral; not simultaneous enforcement of estimated L=-90 m",
            "plane_wind_at_reference_m_s":wind_reference*math.cos(math.radians(delta)),
            "omitted_crosswind_at_reference_m_s":wind_reference*math.sin(math.radians(delta)),
            "wind_projection_angle_deg":delta,
        },
        "plane":{
            "heading_deg_magnetic":heading,
            "axes":"x along original 30-degree jet; z up; cross-plane axis clockwise from x",
            "origin":"equivalent source window centre projected to ground; computational x=0 at window",
            "original_window_horizontal_distance_from_nozzle_m":5.,
            "original_window_centre_xyz_m":deepcopy(b["window_centre_xyz_m"]),
            "cross_plane_depth_m":width,
            "meaning":"2D infinite-slab approximation normalized per metre of depth. The finite source width only converts nominal kg/s to kg/(m s); finite-width side entrainment and omitted crosswind are not represented.",
        },
        "domain":{"length_x_m":16.,"height_m":8.},
        "numerics":{"default_nx":4,"default_nz":4,"smoke_duration_s":.001,"cfl":.2,
                    "conductivity_W_m_K":0.,
                    "conductivity_evidence":"Zero explicit conduction for atmospheric smoke; positive overrides are synthetic numerical coefficients, not measured industrial transport."},
        "boundaries":{"left":"prescribed source flux on exact patch overlap; neutral ambient inflow outside",
                      "right":"open outflow treatment with declared backflow state",
                      "top":"open treatment with declared ambient backflow state",
                      "bottom":"impermeable, free-slip, adiabatic approximation"},
        "original_reported_equivalent_source":{"temperature_K":196.,"propane_mole_fraction":.2,
              "speed_m_s":18.1,"width_m":.78,"height_m":.39,"area_m2":.3042,
              "meaning":"Reported rounded equivalent-source record preserved separately; H00 is not a measured correction."},
        "evidence":{
            "selected_database_inputs":["wind 2.73 m/s at 6 m (revised)", "wind-from 197.73 degrees", "z0 0.006 m", "283.05 K", "102500 Pa", "RH 99%"],
            "assumptions":["neutral shifted-log profile","pressure datum at ground","source window placement/height","2D slab and crosswind omission","free-slip adiabatic ground","short smoke duration and domain"],
            "calculated":["H00 temperature and phase state","flow-consistent source geometry","per-depth component/energy/momentum flux","projected wind","neutral friction velocity"]
        },
        "comparison_policy":{
            "historical_averaging_s":150.,
            "full_release_duration_discrepancy_s":[150.,360.],
            "actual_historical_averaging_indices_known":False,
            "policy":"Future developed unfenced plume comparison, not a fresh 150-second pulse. Current short 2D smoke is not this comparison.",
            "receptors":"30 original 3D sensor positions are not reduced or fitted to this 2D plane.",
        },
        "limitations":[
            "No finite-width crosswind dispersion; projected weather does not recover oblique 3D flow.",
            "No turbulence closure or maintained turbulent atmospheric boundary layer.",
            "Short domain/time and coarse smoke grid do not resolve EEC550 concentration footprints.",
            "Source composition, position and time assumptions remain unresolved historically.",
            "Open boundary reflections and backflow behaviour require numerical checks; no nonreflecting claim.",
            "No terrain, operational safety or Adoshi reconstruction claim.",
        ],
    }
    validate_eec550_case(case)
    return case


def neutral_wind_at_height(z_m, case):
    """Along-plane speed; preserves the recorded shifted-log convention."""
    z = _number(z_m,"height",minimum=0.)
    a = case["atmosphere"]
    speed = a["friction_velocity_m_s"]/a["kappa"]*math.log1p(z/a["roughness_length_m"])
    return speed*math.cos(math.radians(a["wind_projection_angle_deg"]))


def neutral_wind_cell_mean(lower_m, upper_m, case):
    """Analytic cell mean of the projected shifted log wind, not rho-weighted."""
    lower = _number(lower_m,"lower height",minimum=0.)
    upper = _number(upper_m,"upper height",positive=True)
    if upper <= lower:
        raise ValueError("Cell upper height must exceed lower height")
    a = case["atmosphere"]; z0=a["roughness_length_m"]
    def primitive(z):
        return (z+z0)*math.log1p(z/z0)-(z+z0)
    return (a["friction_velocity_m_s"]/a["kappa"]*
            (primitive(upper)-primitive(lower))/(upper-lower)*
            math.cos(math.radians(a["wind_projection_angle_deg"])))


def source_face_overlaps(z_faces_m, case):
    """Exact conservative patch intersection and centroid for each inlet face."""
    faces = [_number(v,"face height",minimum=0.) for v in z_faces_m]
    if len(faces)<2 or any(b<=a for a,b in zip(faces,faces[1:])):
        raise ValueError("Face heights must be strictly increasing")
    s=case["source"]
    lo=s["centre_height_m"]-.5*s["height_m"]
    hi=s["centre_height_m"]+.5*s["height_m"]
    if faces[0]>lo or faces[-1]<hi:
        raise ValueError("Grid must cover the full source patch")
    lengths=[];centres=[];fractions=[]
    for a,b in zip(faces,faces[1:]):
        left=max(a,lo);right=min(b,hi);width=max(0.,right-left)
        lengths.append(width)
        centres.append(.5*(left+right) if width else .5*(a+b))
        fractions.append(width/(b-a))
    return {"fractions":fractions,"overlap_lengths_m":lengths,"overlap_centres_m":centres,
            "patch_lower_m":lo,"patch_upper_m":hi}


def validate_eec550_case(case):
    """Reject inconsistent input contracts; this does not validate field physics."""
    if not isinstance(case,dict) or type(case.get("schema_version")) is not int or case["schema_version"]!=1:
        raise ValueError("Unsupported EEC550 case schema")
    if case.get("faithful_reproduction") is not False or case.get("sensor_comparison_ready") is not False:
        raise ValueError("2D setup must not claim faithful reproduction or sensor readiness")
    try:
        s=case["source"];a=case["atmosphere"];d=case["domain"];plane=case["plane"]
        required_positive = {
            "density":s["density_kg_m3"],"source height":s["height_m"],"source width":s["width_m"],
            "source area":s["area_m2"],"speed":s["speed_m_s"],"mass":s["total_mass_flow_kg_s"],
            "source pressure":s["pressure_Pa"],"source temperature":s["temperature_K"],
            "domain length":d["length_x_m"],"domain height":d["height_m"],
            "reference wind":a["wind_reference_speed_m_s"],"wind reference height":a["wind_reference_height_m"],
            "roughness":a["roughness_length_m"],"kappa":a["kappa"],"ambient density":a["density_at_ground_kg_m3"],
            "ground pressure":a["ground_pressure_Pa"],"ambient temperature":a["temperature_K"],
        }
        for key,v in required_positive.items():_number(v,key,positive=True)
        _number(s["thermal_enthalpy_J_kg"],"enthalpy")
        centre=_number(s["centre_height_m"],"source centre",positive=True)
        if centre-.5*s["height_m"]<0 or centre+.5*s["height_m"]>d["height_m"]:
            raise ValueError("Source patch must fit above ground within domain")
        def close(x,y,label,tol=1e-10):
            x=_number(x,label);y=_number(y,label)
            if not math.isclose(x,y,rel_tol=tol,abs_tol=tol):
                raise ValueError("Inconsistent "+label)
        phases=s["phase_mass_fractions"]
        if set(phases)!={"gas","water_ice","water_liquid","propane_liquid"}:
            raise ValueError("Four phase fractions required")
        for fraction in phases.values():
            if not 0<=_number(fraction,"phase fraction")<=1:raise ValueError("Invalid phase fraction")
        close(sum(phases.values()),1.,"phase fraction sum")
        canonical,_ = _record("data/public/eec550-dispersion-handoff.json")
        cb=canonical["boundary"]
        for key, original in [("temperature_K","temperature_K"),("pressure_Pa","pressure_Pa"),
                              ("density_kg_m3","bulk_density_kg_m3"),("thermal_enthalpy_J_kg","thermal_enthalpy_J_kg"),
                              ("speed_m_s","speed_m_s"),("height_m","window_height_m"),
                              ("width_m","window_width_m"),("area_m2","window_area_m2")]:
            close(s[key],cb[original],"frozen H00 "+key)
        for key, masskey in [("gas","gas_mass_kg_s"),("water_ice","ice_mass_kg_s"),
                             ("water_liquid","liquid_water_mass_kg_s"),("propane_liquid","liquid_propane_mass_kg_s")]:
            close(phases[key],cb[masskey]/cb["total_mass_kg_s"],"frozen H00 phase "+key)
        for key,value in {"temperature_K":283.05,"relative_humidity":.99,"ground_pressure_Pa":102500.,
                          "pressure_datum_height_m":0.,"wind_reference_speed_m_s":2.73,
                          "wind_reference_height_m":6.,"roughness_length_m":.006,"kappa":.4,
                          "wind_from_deg_magnetic":197.73}.items():
            close(a[key],value,"selected v1 weather "+key)
        canonical_study,_ = _record("data/public/eec550-research-bundle-v1/study.json")
        canonical_ambient=next(p["ambient"] for p in canonical_study["paths"]
                               if p["source_id"]=="H00" and p["ambient"]["relative_humidity"]==.99)
        close(a["density_at_ground_kg_m3"],canonical_ambient["bulk_density_kg_m3"],"ambient density lineage")
        masses=s["total_component_mass_kg_s"];fractions=s["component_mass_fractions"]
        if set(masses)!=set(COMPONENTS) or set(fractions)!=set(COMPONENTS):
            raise ValueError("Five declared components required")
        for component in COMPONENTS:
            _number(masses[component],"component mass",minimum=0.)
            close(masses[component],cb["total_component_mass_kg_s"][component],"frozen H00 component "+component)
            _number(fractions[component],"mass fraction",minimum=0.)
            close(fractions[component],masses[component]/s["total_mass_flow_kg_s"],"component fraction")
            close(s["per_depth"]["component_mass_kg_m_s"][component],
                  masses[component]/s["width_m"],"component per-depth flux")
        close(sum(masses.values()),s["total_mass_flow_kg_s"],"total mass")
        close(sum(fractions.values()),1.,"mass fraction sum")
        close(s["propane_mass_flow_kg_s"],masses["C3"],"propane flow")
        close(s["area_m2"],s["width_m"]*s["height_m"],"window area")
        close(s["density_kg_m3"]*s["speed_m_s"]*s["area_m2"],s["total_mass_flow_kg_s"],"source mass-area-speed")
        close(s["per_depth"]["total_mass_kg_m_s"],s["total_mass_flow_kg_s"]/s["width_m"],"per-depth mass")
        close(s["per_depth"]["propane_mass_kg_m_s"],masses["C3"]/s["width_m"],"per-depth propane")
        close(s["per_depth"]["advective_momentum_N_m"],s["total_mass_flow_kg_s"]/s["width_m"]*s["speed_m_s"],"advective momentum")
        close(s["per_depth"]["pressure_traction_N_m"],s["pressure_Pa"]*s["height_m"],"pressure traction")
        close(s["per_depth"]["full_normal_momentum_N_m"],s["per_depth"]["advective_momentum_N_m"]+s["per_depth"]["pressure_traction_N_m"],"full momentum")
        close(s["per_depth"]["enthalpy_plus_kinetic_W_m"],s["total_mass_flow_kg_s"]/s["width_m"]*(s["thermal_enthalpy_J_kg"]+.5*s["speed_m_s"]**2),"energy flux")
        close(s["per_depth"]["potential_energy_W_m"],s["total_mass_flow_kg_s"]/s["width_m"]*9.81*centre,"potential energy flux")
        close(plane["cross_plane_depth_m"],s["width_m"],"slab depth")
        if not 0<=a["relative_humidity"]<=1:raise ValueError("Invalid RH")
        close(a["friction_velocity_m_s"],a["kappa"]*a["wind_reference_speed_m_s"]/math.log1p(a["wind_reference_height_m"]/a["roughness_length_m"]),"neutral friction velocity")
        delta=(a["downwind_deg_magnetic"]-plane["heading_deg_magnetic"]+180.)%360.-180.
        close(a["wind_projection_angle_deg"],delta,"wind projection angle")
        close(a["downwind_deg_magnetic"],(a["wind_from_deg_magnetic"]+180.)%360.,"wind from-to conversion")
        close(a["plane_wind_at_reference_m_s"],neutral_wind_at_height(a["wind_reference_height_m"],case),"projected reference wind")
        close(a["omitted_crosswind_at_reference_m_s"],a["wind_reference_speed_m_s"]*math.sin(math.radians(delta)),"omitted crosswind")
        for key in ["wind_from_deg_magnetic","downwind_deg_magnetic"]:
            if not 0<=_number(a[key],key)<360:raise ValueError("Azimuth must lie in [0,360)")
        if not 0<=_number(plane["heading_deg_magnetic"],"plane heading")<360:
            raise ValueError("Plane azimuth must lie in [0,360)")
        hydro=a["ground_pressure_Pa"]*math.exp(-9.81*a["density_at_ground_kg_m3"]/a["ground_pressure_Pa"]*centre)
        close(s["hydrostatic_ambient_pressure_at_centre_Pa"],hydro,"hydrostatic source ambient pressure")
        close(s["pressure_excess_at_centre_Pa"],s["pressure_Pa"]-hydro,"pressure excess")
        _number(case["numerics"]["smoke_duration_s"],"smoke duration",positive=True)
    except (KeyError,TypeError,OverflowError) as exc:
        raise ValueError("Malformed EEC550 case contract") from exc
    return {"passed":True,"meaning":"Input/ledger checks only, not experimental validation"}
