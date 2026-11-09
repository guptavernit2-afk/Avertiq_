"""Independent mole-basis and rectangle-overlap checks for the refinement report."""
from pathlib import Path
import runpy

import pytest

module = runpy.run_path(str(Path(__file__).resolve().parents[1]/"tools"/"receptor_refinement.py"))
fraction = module["gas_propane_mol_percent"]
summarize = module["summarize_grids"]
M = {"C3":.044097,"N2":.028013,"O2":.031999,"AR":.039948,"H2O":.018015}


def test_phase_correction_includes_liquid_propane_and_all_water_condensates():
    component_masses = {"C3":.3,"N2":.3,"O2":0.,"AR":0.,"H2O":.4}
    cell = {"component_mol_per_kg":{k:component_masses[k]/M[k] for k in M},
            "phase_mass_fractions":{"gas":.5,"propane_liquid":.2,"water_liquid":.15,"water_ice":.15}}
    expected = 100*(.1/M["C3"])/(.1/M["C3"]+.3/M["N2"]+.1/M["H2O"])
    assert fraction(cell,M) == pytest.approx(expected)
    cell["phase_mass_fractions"].update(gas=.25,propane_liquid=.45)
    with pytest.raises(ValueError,match="exceeds"):
        fraction(cell,M)


def grid(nx,nz):
    cells = []
    for j in range(nz):
        for i in range(nx):
            x,z = (i+.5)*2/nx,(j+.5)/nz
            # Same piecewise-constant physical field on 2x2 and 4x4 meshes.
            y = .1*(x>=1.)+.2*(z>=.5)
            mw = y*M["C3"]+(1-y)*M["N2"]
            n = {k:0. for k in M}
            n.update(C3=y/mw,N2=(1-y)/mw)
            cells.append({"x_m":x,"z_m":z,"component_mol_per_kg":n,"phase_mass_fractions":
                          {"gas":1.,"propane_liquid":0.,"water_liquid":0.,"water_ice":0.}})
    return {"cells":cells,"configuration":{"nx":nx,"nz":nz,"length_x_m":2.,"height_m":1.,
            "duration_s":.001,"gravity_m_s2":9.81,"conductivity_W_m_K":0.,"cfl":.2,"boundary":"open"}}


def test_partial_area_weights_preserve_mean_across_meshes():
    result = summarize([grid(2,2),grid(4,4)],M,(.25,1.5,.2,.75))["grids"]
    expected = (10*.5*.3+20*.75*.25+30*.5*.25)/(1.25*.55)
    for row in result:
        assert row["box_mean_gas_propane_mol_percent"] == pytest.approx(expected)
        assert row["peak_gas_propane_mol_percent"] == pytest.approx(30.)
    assert result[1]["box_mean_change_percentage_points"] == pytest.approx(0.,abs=1e-12)


def test_mismatched_time_or_missing_coverage_refused():
    a,b = grid(2,2),grid(4,4)
    with pytest.raises(ValueError,match="outside"):
        summarize([a,b],M,(0,3,0,1))
    b["configuration"]["duration_s"] = .002
    with pytest.raises(ValueError,match="matched"):
        summarize([a,b],M,(0,2,0,1))
