"""Small-amplitude dry-gas acoustic refinement benchmark, not field validation."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from avertiq_equilibrium.properties import Properties
from avertiq_equilibrium.equilibrium import Equilibrium
from avertiq_equilibrium.thermal_flow import solve_thermal_flow
from avertiq_equilibrium.cases import provenance

def run():
    props=Properties()
    eq=Equilibrium(props)
    component=1  # Pure N2 ideal carrier, no condensate.
    temperature=260.
    pressure=102500.
    n=np.zeros(5)
    n[component]=1/props.mw[component]
    base=eq.tp(temperature,pressure,n)
    rho=base.mass_kg/base.volume_m3
    cp=(props.gas_h(temperature+.01,component)-props.gas_h(temperature-.01,component))/.02/props.mw[component]
    gas_constant=props.r/props.mw[component]
    cv=cp-gas_constant
    sound=math.sqrt(cp/cv*gas_constant*temperature)
    amplitude=.1
    duration=1e-4
    length=1.
    wavenumber=2*math.pi/length
    rows=[]
    for cells in (8,16,32):
        dx=length/cells
        x=(np.arange(cells)+.5)*dx
        # Exact linearized cell averages; nonlinear initialization errors are O(amplitude^2).
        wave=np.sinc(wavenumber*dx/(2*math.pi))*np.sin(wavenumber*x)
        dp=amplitude*wave
        densities=rho+dp/sound**2
        speeds=dp/(rho*sound)
        q=np.zeros((cells,7))
        for j in range(cells):
            p=pressure+dp[j]
            t=p/(densities[j]*gas_constant)
            state=eq.tp(t,p,n)
            internal=state.enthalpy_J-p*state.volume_m3
            q[j,component]=densities[j]
            q[j,5]=densities[j]*speeds[j]
            q[j,6]=densities[j]*(internal+.5*speeds[j]**2)
        result=solve_thermal_flow(q,properties=props,length_m=length,duration_s=duration,
                                  conductivity_W_m_K=0.)
        exact=pressure+amplitude*np.sinc(wavenumber*dx/(2*math.pi))*np.sin(wavenumber*(x-sound*duration))
        predicted=np.array([cell["pressure_Pa"] for cell in result["cells"]])
        error=float(np.sqrt(np.mean((predicted-exact)**2)))
        rows.append({"cells":cells,"pressure_RMSE_Pa":error,
                     "normalized_pressure_RMSE":error/amplitude,
                     "conservation":result["diagnostics"]["maximum_relative_conservation_residual"]})
    if not rows[2]["pressure_RMSE_Pa"]<rows[1]["pressure_RMSE_Pa"]<rows[0]["pressure_RMSE_Pa"]:
        raise RuntimeError("Acoustic refinement failed to reduce error")
    return {"schema_version":1,"passed":True,
            "scope":"Linearized pure-N2 acoustic verification; not multiphase or EEC550 validation",
            "temperature_K":temperature,"pressure_Pa":pressure,"pressure_amplitude_Pa":amplitude,
            "duration_s":duration,"length_m":length,"analytic_sound_speed_m_s":sound,
            "initialization":"Linearized right-going cell averages; nonlinear terms O(amplitude squared)",
            "cases":rows,"provenance":provenance(),
            "benchmark_script_sha256_LF":hashlib.sha256(Path(__file__).read_text(encoding="utf-8").encode("utf-8")).hexdigest()}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        parser.error("Use a fresh output path")
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as handle:
        handle.write(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print("PASS acoustic refinement:", [(x["cells"],x["pressure_RMSE_Pa"]) for x in result["cases"]])
