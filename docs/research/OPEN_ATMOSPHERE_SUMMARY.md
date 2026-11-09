# EEC550 open-domain checkpoint

The conditional H00 release now enters a vertical slice through a 0.393 m high window. The neutral wind profile uses the reported 2.73 m/s wind at 6 m. Its along-jet component is 2.668 m/s. The assumed window centre is 0.5 m above ground. Projecting the finite source into this slice gives **3.8195 kg of propane per second per metre of depth**. The inlet integrates the exact window overlap on each grid face. [Inputs and assumptions](EEC550_ATMOSPHERIC_SETUP.md)

The right and upper boundaries extrapolate outward flow and admit ambient air on backflow. The ground is impermeable and adiabatic. Separate controls verify that an outlet-adjacent tracer leaves the domain, incoming air enters on flow reversal, and the source-free wind profile holds steady. Conservation checks include the actual flux through all four sides and the gravitational impulse. **295 tests and 283 atmospheric checks passed.** [Boundary checks](../../data/public/eec550-open-atmosphere-v1/checks.json)

## What changed with the grid

Every result below is a startup snapshot at **0.001 s**. The mean uses the same rectangle from 0 to 4 m downstream and 0 to 0.8 m above ground. It averages gas-phase propane mole percent by cell overlap after accounting for condensed propane and water. The peak is the highest cell value in that run.

| Domain and refinement | Cells across source height | Peak gas propane (mol%) | Mean in fixed rectangle (mol%) |
|---|---:|---:|---:|
| 16 × 8 m, 4 × 4 | 0.196 | 0.02483 | 0.02483 |
| 16 × 8 m, 8 × 8 | 0.393 | 0.09897 | 0.04950 |
| 16 × 8 m, 12 × 12 | 0.589 | 0.20487 | 0.05788 |
| 16 × 1.6 m, 4 × 4 | 0.982 | 0.09341 | 0.06193 |
| 16 × 1.6 m, 4 × 8 | 1.964 | 0.12592 | 0.06191 |
| 16 × 1.6 m, 4 × 16 | 3.927 | 0.12591 | 0.06187 |

**The larger-domain concentration field remains sensitive to grid size.** Its propane inventory agrees across grids because the prescribed injection rate is conserved. On the 4 × 4 grid, reducing CFL from 0.2 to 0.1 to 0.05 gives 2, 3 and 6 steps. Peak pressure departure changes from 91.12 to 88.83 to 87.70 Pa. [Main grid and time study](../../data/public/eec550-open-atmosphere-v1/refinement.json) · [Gas concentration results](../../data/public/eec550-open-atmosphere-v1/gas-concentration.json)

For the aperture study I chose a lower top boundary, fixed 4 m horizontal spacing and **25 equal 0.00004 s steps**. The last two vertical grids agree closely on the peak. Horizontal resolution, domain height and longer-time behaviour still need independent tests before using a concentration at a receptor. [Aperture runs](../../data/public/eec550-open-atmosphere-v1/aperture.json) · [Gas concentration results](../../data/public/eec550-open-atmosphere-v1/aperture-gas-concentration.json)

## Before field comparison

The experiment calls for developed-plume concentrations at 30 three-dimensional receptor positions with a 150 s averaging window. The present slice omits lateral spreading and the projected crosswind component of 0.58 m/s. The prescribed source flux, assumed source height, possible acoustic reflections and inviscid wind profile also limit interpretation. A field score requires a resolved plume, suitable atmospheric transport and matched sampling.

## Reproduce from Avertiq_

Use the existing environment and fresh output paths.

~~~powershell
.\.venv\Scripts\python.exe -m pytest research/equilibrium -q
.\.venv\Scripts\python.exe -m avertiq_equilibrium atmospheric-checks --output outputs/my-checks.json
.\.venv\Scripts\python.exe -m avertiq_equilibrium atmospheric --output outputs/my-flow.json
.\.venv\Scripts\python.exe -m avertiq_equilibrium atmospheric-refinement --output outputs/my-grids.json
.\.venv\Scripts\python.exe research/equilibrium/tools/aperture_refinement.py --output outputs/my-aperture.json
.\.venv\Scripts\python.exe research/equilibrium/tools/receptor_refinement.py --input outputs/my-grids.json --output outputs/my-grid-gas.json
.\.venv\Scripts\python.exe research/equilibrium/tools/receptor_refinement.py --input outputs/my-aperture.json --output outputs/my-aperture-gas.json
~~~
