"""Independent numerical checks for the frozen-endpoint buoyant flow stage.

Checks verify the implemented discrete hydrodynamics, not experimental dispersion,
phase equilibrium in moving cells, or an EEC550 source/atmosphere reproduction.
"""
import math
import numpy as np

from . import flow
from .cases import provenance


def _divergence(u, w, dx, dz):
    """Independent face-flux divergence; x is periodic, vertical walls closed."""
    return (np.roll(u, -1, axis=1)-u)/dx+(w[1:]-w[:-1])/dz


def run_flow_checks():
    checks = []

    def bounded(name, measured, tolerance, units):
        value = float(measured)
        passed = math.isfinite(value) and abs(value) <= tolerance
        checks.append({"name": name, "measured": value, "maximum_absolute": tolerance,
                       "units": units, "passed": passed})
        if not passed:
            raise RuntimeError(f"Flow check failed: {name}: {value}")

    def positive(name, measured, minimum, units):
        value = float(measured)
        passed = math.isfinite(value) and value > minimum
        checks.append({"name": name, "measured": value, "must_exceed": minimum,
                       "units": units, "passed": passed})
        if not passed:
            raise RuntimeError(f"Flow check failed: {name}: {value}")

    nz, nx = 10, 12
    dx, dz = .5, .4
    rng = np.random.default_rng(421)
    u = rng.normal(size=(nz, nx))
    w = rng.normal(size=(nz+1, nx))
    w[0] = w[-1] = 0.
    rho = 1.+rng.uniform(0., 1., size=(nz, nx))
    before = float(np.max(abs(_divergence(u,w,dx,dz))))
    projected_u, projected_w, pressure, audit = flow.project_velocity(u,w,rho,dx,dz,.02)
    after = float(np.max(abs(_divergence(projected_u,projected_w,dx,dz))))
    bounded("variable-density projected divergence", after, 1e-8, "1/s")
    bounded("projection divergence reduction ratio", after/before, 1e-9, "1")
    bounded("impermeable bottom", np.max(abs(projected_w[0])), 1e-12, "m/s")
    bounded("impermeable top", np.max(abs(projected_w[-1])), 1e-12, "m/s")
    if not np.isfinite(pressure).all():
        raise RuntimeError("Flow check failed: nonfinite pressure")

    shape = (12, 12)
    z = (np.arange(shape[0])+.5)*10/shape[0]
    x = (np.arange(shape[1])+.5)*10/shape[1]
    blob = .75*np.exp(-((x[None,:]-5.)**2+(z[:,None]-6.5)**2)/1.5)
    options = dict(rho_light=1.,rho_heavy=2.,length_x_m=10.,height_m=10.,
                   duration_s=.25,viscosity_m2_s=.01)
    gravity = flow.simulate_flow(blob,gravity_m_s2=9.81,**options)
    control = flow.simulate_flow(blob,gravity_m_s2=0.,**options)
    stratified = np.broadcast_to(np.linspace(.8,.1,shape[0])[:,None],shape).copy()
    hydrostatic = flow.simulate_flow(stratified,gravity_m_s2=9.81,**options)

    def centroid(fraction):
        return float(np.sum(fraction*z[:,None])/np.sum(fraction))

    initial_centroid = centroid(blob)
    gravity_centroid = centroid(np.asarray(gravity["final_fraction"]))
    control_centroid = centroid(np.asarray(control["final_fraction"]))
    positive("dense-blob descent relative to zero gravity",
             control_centroid-gravity_centroid, 1e-5, "m")
    bounded("zero-gravity centroid drift", control_centroid-initial_centroid,1e-10,"m")
    bounded("hydrostatic horizontal velocity",
            np.max(abs(np.asarray(hydrostatic["u_face_m_s"]))),1e-8,"m/s")
    bounded("hydrostatic vertical velocity",
            np.max(abs(np.asarray(hydrostatic["w_face_m_s"]))),1e-8,"m/s")

    for label, case in (("gravity",gravity),("zero_gravity",control),("hydrostatic",hydrostatic)):
        initial = np.asarray(case["initial_fraction"])
        final = np.asarray(case["final_fraction"])
        density = np.asarray(case["density_kg_m3"])
        bounded(label+" volume-fraction sum residual",final.sum()-initial.sum(),1e-9,"cell fraction sum")
        bounded(label+" density relation",np.max(abs(density-(1.+final))),1e-12,"kg/m3")
        bounded(label+" density mass budget",(density.sum()-(1.+initial).sum())/(1.+initial).sum(),1e-10,"1")
        bounded(label+" final divergence",
                np.max(abs(_divergence(np.asarray(case["u_face_m_s"]),np.asarray(case["w_face_m_s"]),10/shape[1],10/shape[0]))),
                1e-8,"1/s")
        if not np.isfinite(final).all() or final.min() < -1e-12 or final.max() > 1+1e-12:
            raise RuntimeError("Flow check failed: inadmissible fraction")

    reference = flow.run_flow(nx=12,nz=12,duration_s=.1)
    reference_density = np.asarray(reference["density_kg_m3"])
    positive("ThermoPack-anchored density contrast",
             float(reference_density.max()-reference_density.min()),1e-3,"kg/m3")
    bounded("ThermoPack-anchored mass budget",
            reference["diagnostics"]["relative_mass_residual"],1e-10,"1")

    return {
        "schema_version":1,"passed":True,
        "scope":"Numerical verification of frozen-endpoint variable-density incompressible flow; not HEM energy coupling or field validation.",
        "checks":checks,
        "projection":{"initial_max_divergence_s_inv":before,
                      "final_max_divergence_s_inv":after,"solver_audit":audit},
        "synthetic_cases":{"gravity":gravity,"zero_gravity":control,"hydrostatic":hydrostatic},
        "thermodynamic_endpoint_case":reference,
        "provenance":provenance(),
    }
