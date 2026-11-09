"""Compare gas-phase propane mole percent on matched open-slice grids."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

COMPONENTS = ("C3", "N2", "O2", "AR", "H2O")
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BOX = (0., 4., 0., .8)


def gas_propane_mol_percent(cell, masses):
    """Reconstruct gas moles on the same kg-mixture basis as the saved cell."""
    n = cell["component_mol_per_kg"]
    phases = cell["phase_mass_fractions"]
    if (set(n) != set(COMPONENTS) or set(masses) != set(COMPONENTS)
            or set(phases) != {"gas", "propane_liquid", "water_liquid", "water_ice"}):
        raise ValueError("Incomplete component or phase record")
    if (any(not math.isfinite(x) or x < 0 for x in n.values())
            or any(not math.isfinite(x) or x <= 0 for x in masses.values())
            or any(not math.isfinite(x) or not 0 <= x <= 1 for x in phases.values())
            or not math.isclose(sum(phases.values()), 1., abs_tol=1e-8)
            or not math.isclose(sum(n[k]*masses[k] for k in COMPONENTS), 1., abs_tol=1e-8)):
        raise ValueError("Invalid one-kilogram phase/component ledger")
    gas = dict(n)
    gas["C3"] -= phases["propane_liquid"]/masses["C3"]
    gas["H2O"] -= (phases["water_liquid"] + phases["water_ice"])/masses["H2O"]
    for k, amount in gas.items():
        if amount < -1e-11*max(n[k], 1.):
            raise ValueError("Condensed inventory exceeds component total")
        gas[k] = max(amount, 0.)  # Only an arithmetic roundoff residual can reach here.
    if phases["gas"] == 0 or sum(gas.values()) <= 0:
        raise ValueError("A gas phase is required for a gas concentration")
    return 100.*gas["C3"]/sum(gas.values())


def summarize_grids(runs, molar_masses_kg_mol, box=DEFAULT_BOX):
    """Area average of the cellwise mole percent over one fixed rectangle in metres."""
    if len(runs) < 2:
        raise ValueError("At least two spatial grids are required")
    x0, x1, z0, z1 = box
    if not all(math.isfinite(v) for v in box) or not (0 <= x0 < x1 and 0 <= z0 < z1):
        raise ValueError("Invalid sampling rectangle")
    reference = runs[0]["configuration"]
    fixed = ("length_x_m", "height_m", "duration_s", "gravity_m_s2", "conductivity_W_m_K", "cfl", "boundary")
    area = (x1-x0)*(z1-z0)
    seen = set()
    result = []
    for run in runs:
        config = run["configuration"]
        if any(config[k] != reference[k] for k in fixed):
            raise ValueError("Spatial comparison requires matched time, domain and physics settings")
        nx, nz = config["nx"], config["nz"]
        if (type(nx) is not int or type(nz) is not int or min(nx,nz) < 1 or
                (nx,nz) in seen or len(run["cells"]) != nx*nz):
            raise ValueError("Invalid or repeated grid")
        seen.add((nx,nz))
        if x1 > config["length_x_m"] or z1 > config["height_m"]:
            raise ValueError("Sampling rectangle lies outside the computational domain")
        dx, dz = config["length_x_m"]/nx, config["height_m"]/nz
        covered = 0.
        integral = 0.
        peak = 0.
        covered_cells = 0
        for index, cell in enumerate(run["cells"]):
            j, i = divmod(index, nx)
            if (not math.isclose(cell["x_m"], (i+.5)*dx, abs_tol=1e-10) or
                    not math.isclose(cell["z_m"], (j+.5)*dz, abs_tol=1e-10)):
                raise ValueError("Cell layout differs from the stated Cartesian grid")
            percent = gas_propane_mol_percent(cell,molar_masses_kg_mol)
            overlap = (max(0., min((i+1)*dx,x1)-max(i*dx,x0)) *
                       max(0., min((j+1)*dz,z1)-max(j*dz,z0)))
            peak = max(peak,percent)
            covered += overlap
            covered_cells += int(overlap > 0)
            integral += percent*overlap
        if not math.isclose(covered,area,rel_tol=1e-11):
            raise ValueError("Incomplete coverage of the sampling rectangle")
        mean = integral/area
        previous = result[-1] if result else None
        result.append({"nx":nx,"nz":nz,"dx_m":dx,"dz_m":dz,"overlapping_cells":covered_cells,
                       "peak_gas_propane_mol_percent":peak,
                       "box_mean_gas_propane_mol_percent":mean,
                       "box_mean_change_percentage_points":mean-previous["box_mean_gas_propane_mol_percent"]
                           if previous else None})
    return {"schema_version":1,"duration_s":reference["duration_s"],
            "rectangle_m":{"x_min":x0,"x_max":x1,"z_min":z0,"z_max":z1},
            "quantity":"100 * gas C3 moles / total gas moles, with liquid propane, liquid water and ice removed",
            "averaging":"Area-weighted mean of piecewise-constant final cell mole percentages using exact cell/rectangle overlap",
            "interpretation":"Inlet-adjacent spatial startup diagnostic; experimental receptor basis and historical 150 s timing still require matching.",
            "grids":result}


def read_record(path):
    data = path.read_bytes()
    normalized = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return json.loads(normalized), {"name":path.name, "sha256_exact_bytes":sha256(data).hexdigest(),
                                    "sha256_UTF8_LF":sha256(normalized.encode("utf-8")).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True,help="Grid refinement JSON with grid_runs")
    parser.add_argument("--molar-masses",type=Path,default=ROOT/"data/public/eec550-equilibrium-results.json")
    parser.add_argument("--box",nargs=4,type=float,metavar=("X0","X1","Z0","Z1"),default=DEFAULT_BOX)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("Choose a fresh output path")
    grids, grid_source = read_record(args.input)
    properties, property_source = read_record(args.molar_masses)
    summary = summarize_grids(grids["grid_runs"],properties["molar_masses_kg_mol"],args.box)
    summary["provenance"] = {"grid_record":grid_source,"molar_mass_record":property_source,
                             "script_sha256_UTF8_LF":sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest()}
    payload = json.dumps(summary,indent=2,allow_nan=False)+"\n"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8",newline="\n") as handle:
        handle.write(payload)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
