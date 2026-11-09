"""Open-boundary vertical-slice research configuration, not a field prediction.

Inflow reservoir plus prescribed conservative source flux; extrapolating
right/top outflow and ambient-reservoir backflow. No nonreflecting claim.
"""
import copy
import math
import numpy as np

from .properties import Properties
from .equilibrium import Equilibrium
from .thermal2d import initialize_thermal2d, solve_thermal2d, _number
from .study import ambient_stream

def choose_open_ghost(interior, ambient, normal_index, outward_sign, tolerance=1e-8):
    """Select an exterior gas-energy state; this does not prescribe actual flux."""
    inside=np.asarray(interior,dtype=float)
    reservoir=np.asarray(ambient,dtype=float)
    if (inside.shape!=(8,) or reservoir.shape!=(8,) or normal_index not in (5,6)
            or outward_sign not in (-1,1) or not math.isfinite(tolerance) or tolerance<0
            or not np.isfinite(inside).all() or not np.isfinite(reservoir).all()
            or min(inside[:5])<0 or min(reservoir[:5])<0
            or inside[:5].sum()<=0 or reservoir[:5].sum()<=0):
        raise ValueError("Invalid open-boundary state or orientation")
    velocity=inside[normal_index]/inside[:5].sum()
    if outward_sign*velocity >= -tolerance:
        return inside.copy(),"extrapolated_outflow"
    return reservoir.copy(),"ambient_reservoir_backflow"

class AtmosphericBoundary:
    """Boundary operator and auditable exact prescribed-source face integrals."""
    limitations=[
        "2D plane-source approximation; finite-width/crosswind dispersion is absent.",
        "Prescribed source flux and reservoir inflow can reflect acoustic waves.",
        "Right/top zero-gradient outflow with ambient backflow is not proven nonreflecting.",
        "Inlet log wind is prescribed; inviscid ground has no rough-wall stress or turbulence closure.",
        "Short transient numerical test, not a developed EEC550 150-second comparison.",
        "No terrain, ground heat transfer or cross-plane receptor validation.",
        "Source overlap flux is exact but subcell source structure/potential distribution is unresolved.",
    ]
    def __init__(self,properties,case,nx,nz,gravity_m_s2=9.81,source_enabled=True):
        from .eec550_case import validate_eec550_case,neutral_wind_cell_mean,source_face_overlaps
        validate_eec550_case(case)
        if any(isinstance(v,bool) or not isinstance(v,int) or not 4<=v<=16 for v in (nx,nz)):
            raise ValueError("nx/nz must be integers from 4 to 16")
        for key,expected in (("temperature_K",283.05),("relative_humidity",.99),("ground_pressure_Pa",102500.)):
            if not math.isclose(case["atmosphere"][key],expected,rel_tol=0.,abs_tol=1e-10):
                raise ValueError("This atmospheric engine requires the reviewed fixed "+key)
        source=case["source"]
        source_y=np.array([source["component_mass_fractions"][k] for k in ("C3","N2","O2","AR","H2O")])
        live=Equilibrium(properties).tp(source["temperature_K"],source["pressure_Pa"],source_y/properties.mw)
        density_error=abs(live.mass_kg/live.volume_m3-source["density_kg_m3"])/source["density_kg_m3"]
        enthalpy_error=abs(live.enthalpy_J/live.mass_kg-source["thermal_enthalpy_J_kg"])
        phases={"gas":float(live.gas_mol@properties.mw)/live.mass_kg,
                "water_ice":live.ice_mol*properties.mw[4]/live.mass_kg,
                "water_liquid":live.water_liquid_mol*properties.mw[4]/live.mass_kg,
                "propane_liquid":live.propane_liquid_mol*properties.mw[0]/live.mass_kg}
        phase_error=max(abs(phases[k]-source["phase_mass_fractions"][k]) for k in phases)
        if density_error>1e-6 or enthalpy_error>1. or phase_error>1e-6:
            raise ValueError("Recorded source is incompatible with live EOS or enthalpy reference; rebuild a mapped case")
        self.source_compatibility={"passed":True,"relative_density_error":float(density_error),
            "enthalpy_error_J_kg":float(enthalpy_error),"maximum_phase_fraction_error":float(phase_error),
            "meaning":"Recorded source matches live TP closure and caloric reference; no arbitrary reference remapping is inferred."}
        self.p=properties;self.case=copy.deepcopy(case);self.nx=nx;self.nz=nz
        self.lx=float(case["domain"]["length_x_m"]);self.height=float(case["domain"]["height_m"])
        self.g=_number(gravity_m_s2,"gravity");self.dx=self.lx/nx;self.dz=self.height/nz
        self.z=(np.arange(nz)+.5)*self.dz
        if not isinstance(source_enabled,bool):
            raise ValueError("source_enabled must be boolean")
        self.source_enabled=source_enabled
        _,ref=initialize_thermal2d(properties,nx=nx,nz=nz,length_x_m=self.lx,
                                  height_m=self.height,gravity_m_s2=self.g,blob=False)
        wind=np.array([neutral_wind_cell_mean(j*self.dz,(j+1)*self.dz,case) for j in range(nz)])
        if np.any(wind<=0):
            raise ValueError("The reviewed inlet requires positive along-plane wind")
        rho=ref["conserved"][:,:,:5].sum(2)
        ref["conserved"][:,:,5]=rho*wind[:,None]
        ref["conserved"][:,:,7]+=.5*rho*wind[:,None]**2
        ref["metadata"]["wind_profile"]="prescribed projected neutral logarithmic inlet"
        self.reference=ref
        self._canonical=copy.deepcopy(ref)
        self.ambient_gas=ref["conserved"].copy()
        self.ambient_gas[:,:,7]-=rho*self.g*self.z[:,None]
        ambient=ambient_stream(properties)
        if not math.isclose(ambient.metadata["bulk_density_kg_m3"],case["atmosphere"]["density_at_ground_kg_m3"],rel_tol=1e-10):
            raise ValueError("Declared ambient density differs from the reviewed thermodynamics")
        self.ambient_pressure=ref["pressure_cells_Pa"].copy()
        self.ambient_sound=np.empty(nz)
        from .equilibrium_uv import EquilibriumUV
        uv=EquilibriumUV(properties)
        for j in range(nz):
            e=self.ambient_gas[j,0,7]/rho[j,0]-.5*wind[j]**2
            state=uv.solve(float(rho[j,0]),ambient.mol_per_kg,float(e),
                           pressure_hint_Pa=float(self.ambient_pressure[j]))
            self.ambient_sound[j]=uv.sound_speed(float(rho[j,0]),ambient.mol_per_kg,float(e),state=state)
        overlap=source_face_overlaps((np.arange(nz+1)*self.dz).tolist(),case)
        self.overlap=overlap
        self.theta=np.asarray(overlap["fractions"],dtype=float)
        self.source_flux=np.zeros((nz,8))
        source=case["source"];ys=np.array([source["component_mass_fractions"][k] for k in ("C3","N2","O2","AR","H2O")])
        density=float(source["density_kg_m3"]);speed=float(source["speed_m_s"])
        mass_flux=density*speed
        for j in range(nz):
            if self.theta[j]>0:
                centre=overlap["overlap_centres_m"][j]
                self.source_flux[j,:5]=mass_flux*ys
                self.source_flux[j,5]=mass_flux*speed+source["pressure_Pa"]
                self.source_flux[j,7]=mass_flux*(source["thermal_enthalpy_J_kg"]+.5*speed**2+self.g*centre)
        self.gross_source_rate=(self.theta[:,None]*self.source_flux).sum(0)*self.dz if source_enabled else np.zeros(8)
        self._reset_flux_history()

    def begin_run(self, nx, nz, length_x_m, height_m, gravity_m_s2):
        """Bind this run's face measures to the configured grid and start its ledger."""
        requested = (nx, nz, length_x_m, height_m, gravity_m_s2)
        configured = (self.nx, self.nz, self.lx, self.height, self.g)
        if requested != configured:
            raise ValueError("Atmospheric boundary grid, domain extents and gravity must match the solve")
        self._reset_flux_history()

    def _reset_flux_history(self):
        self._sides={name:np.zeros(8) for name in ("left","right","bottom","top")}
        self._gross=np.zeros(8);self._excess=np.zeros(8);self._pending_excess=np.zeros(8)
        self.history=[]

    def canonical_reference(self):
        return self._canonical

    def fluxes(self,array,records,riemann):
        nz,nx=self.nz,self.nx
        rho=array[:,:,:5].sum(2)
        gas=array.copy();gas[:,:,7]-=rho*self.g*self.z[:,None]
        pressure=np.array([[r["state"].pressure_Pa for r in line] for line in records])
        sound=np.array([[r["c"] for r in line] for line in records])
        # Left reservoir is always present; the solved Riemann flux outside the
        # source is free to respond to the interior state.
        left_ghost=self.ambient_gas[:,0].copy()
        right_ghost=np.empty((nz,8));pr=np.empty(nz);cr=np.empty(nz)
        for j in range(nz):
            right_ghost[j],mode=choose_open_ghost(gas[j,-1],self.ambient_gas[j,-1],5,1)
            if mode=="ambient_reservoir_backflow":
                pr[j]=self.ambient_pressure[j];cr[j]=self.ambient_sound[j]
            else:pr[j]=pressure[j,-1];cr[j]=sound[j,-1]
        left=np.concatenate([left_ghost[:,None,:],gas],axis=1)
        right=np.concatenate([gas,right_ghost[:,None,:]],axis=1)
        pl=np.concatenate([self.ambient_pressure[:,None],pressure],axis=1)
        pr=np.concatenate([pressure,pr[:,None]],axis=1)
        cl=np.concatenate([self.ambient_sound[:,None],sound],axis=1)
        cr=np.concatenate([sound,cr[:,None]],axis=1)
        fx=riemann(left.reshape(-1,8),right.reshape(-1,8),pl.ravel(),pr.ravel(),cl.ravel(),cr.ravel(),5).reshape(nz,nx+1,8)
        fx[:,:,7]+=self.g*self.z[:,None]*fx[:,:,:5].sum(2)
        bottom=gas[0:1].copy();bottom[:,:,6]*=-1
        top=np.empty((1,nx,8));pt=np.empty(nx);ct=np.empty(nx)
        for i in range(nx):
            top[0,i],mode=choose_open_ghost(gas[-1,i],self.ambient_gas[-1,i],6,1)
            if mode=="ambient_reservoir_backflow":
                pt[i]=self.ambient_pressure[-1];ct[i]=self.ambient_sound[-1]
            else:pt[i]=pressure[-1,i];ct[i]=sound[-1,i]
        lower=np.concatenate([bottom,gas],axis=0)
        upper=np.concatenate([gas,top],axis=0)
        pl=np.concatenate([pressure[0:1],pressure],axis=0)
        pr=np.concatenate([pressure,pt[None,:]],axis=0)
        cl=np.concatenate([sound[0:1],sound],axis=0)
        cr=np.concatenate([sound,ct[None,:]],axis=0)
        fz=riemann(lower.reshape(-1,8),upper.reshape(-1,8),pl.ravel(),pr.ravel(),cl.ravel(),cr.ravel(),6).reshape(nz+1,nx,8)
        fz[:,:,7]+=(self.g*np.arange(nz+1)*self.dz)[:,None]*fz[:,:,:5].sum(2)
        fz[0,:,:5]=0.;fz[0,:,5]=0.;fz[0,:,7]=0.
        return fx,fz

    def physical_reference_fluxes(self):
        bar=self._canonical["conserved"];rho=bar[:,:,:5].sum(2)
        speed=bar[:,:,5]/rho
        physical=bar*speed[:,:,None]
        physical[:,:,5]+=self.ambient_pressure[:,None]
        physical[:,:,7]+=self.ambient_pressure[:,None]*speed
        fx=np.concatenate([physical,physical[:,-1:]],axis=1)
        fz=np.zeros((self.nz+1,self.nx,8))
        fz[:,:,6]=self.reference["pressure_faces_Pa"][:,None]
        return fx,fz

    def apply_source(self,fx):
        before=fx[:,0].copy()
        if self.source_enabled:
            fx[:,0]=(1-self.theta[:,None])*before+self.theta[:,None]*self.source_flux
            self._pending_excess=((fx[:,0]-before).sum(0)*self.dz)
        else:self._pending_excess=np.zeros(8)

    def record_fluxes(self,fx,fz,dt):
        increments={
            "left":dt*self.dz*fx[:,0].sum(0),
            "right":-dt*self.dz*fx[:,-1].sum(0),
            "bottom":dt*self.dx*fz[0].sum(0),
            "top":-dt*self.dx*fz[-1].sum(0),
        }
        for name,value in increments.items():self._sides[name]+=value
        self._gross+=dt*self.gross_source_rate
        self._excess+=dt*self._pending_excess
        net=sum(increments.values(),np.zeros(8))
        self.history.append({"dt_s":float(dt),"net_inward_boundary_increment":net.tolist(),
                             "per_side_inward_increment":{k:v.tolist() for k,v in increments.items()}})

    def summary(self):
        return {
            "case_id":self.case.get("case_id","EEC550 conditional vertical slice"),
            "source_enabled":self.source_enabled,
            "source_thermodynamic_compatibility":self.source_compatibility,
            "source_overlap":self.overlap,
            "prescribed_source_rate_per_m_depth":self.gross_source_rate.tolist(),
            "accumulated_prescribed_source_per_m_depth":self._gross.tolist(),
            "accumulated_source_excess_over_replaced_ambient_per_m_depth":self._excess.tolist(),
            "per_side_accumulated_inward_integrals":{k:v.tolist() for k,v in self._sides.items()},
            "boundary_history":self.history,
            "backflow_state_basis":"Canonical adjacent ambient cell; reference correction maps the hydrostatic face pressure. Near-zero normal velocity uses a 1e-8 m/s switching deadband.",
            "pressure_boundary":"Extrapolated right/top outflow; ambient reservoir on backflow. Not nonreflecting.",
            "actual_source_pressure_excess_at_centre_Pa":float(self.case["source"]["pressure_Pa"]-102500.*math.exp(-self.g*self.reference["metadata"]["density_per_pressure"]*self.case["source"]["centre_height_m"])),
            "ambient_cell_quadrature":"rho cell mean times log-wind cell mean; kinetic energy of mean velocity, not exact density-weighted shear quadrature",
            "source_energy_potential_basis":"Exact overlap-centroid height, not cell-centre height",
            "source_flux_meaning":"Gross prescribed patch flux includes normal pressure traction; excess subtracts the ambient portion it replaces.",
            "source_advective_momentum_rate_per_m_depth":float(self.case["source"]["density_kg_m3"]*self.case["source"]["speed_m_s"]**2*self.case["source"]["height_m"]) if self.source_enabled else 0.,
            "source_pressure_traction_rate_per_m_depth":float(self.case["source"]["pressure_Pa"]*self.case["source"]["height_m"]) if self.source_enabled else 0.,
            "case_configuration":self.case,
        }

def initialize_atmospheric(properties=None,*,nx=None,nz=None,case_config=None,gravity_m_s2=9.81,source_enabled=True):
    from .eec550_case import build_eec550_case
    props=properties or Properties()
    case=build_eec550_case() if case_config is None else case_config
    nx=case["numerics"]["default_nx"] if nx is None else nx
    nz=case["numerics"]["default_nz"] if nz is None else nz
    boundary=AtmosphericBoundary(props,case,nx,nz,gravity_m_s2,source_enabled)
    return boundary.reference["conserved"].copy(),boundary.reference,boundary

def run_atmospheric(properties=None,*,nx=None,nz=None,duration_s=None,cfl=None,case_config=None,
                    source_enabled=True,conductivity_W_m_K=None,gravity_m_s2=9.81,max_timestep_s=None):
    from .eec550_case import build_eec550_case
    props=properties or Properties()
    case=build_eec550_case() if case_config is None else case_config
    numerical=case["numerics"]
    duration_s=numerical["smoke_duration_s"] if duration_s is None else duration_s
    cfl=numerical["cfl"] if cfl is None else cfl
    conductivity_W_m_K=numerical["conductivity_W_m_K"] if conductivity_W_m_K is None else conductivity_W_m_K
    initial,reference,boundary=initialize_atmospheric(props,nx=nx,nz=nz,case_config=case,
        gravity_m_s2=gravity_m_s2,source_enabled=source_enabled)
    result=solve_thermal2d(initial,properties=props,length_x_m=boundary.lx,height_m=boundary.height,
        duration_s=duration_s,cfl=cfl,conductivity_W_m_K=conductivity_W_m_K,
        gravity_m_s2=gravity_m_s2,reference=reference,atmosphere=boundary,max_timestep_s=max_timestep_s)
    result["model"]="2D conditional open-boundary Euler-HLLC/Fourier/gravity with equilibrium UV EOS; EEC550 vertical slice"
    result["initial_condition"]="Isothermal hydrostatic ambient with prescribed projected neutral log wind"
    result["atmospheric"]["runtime_numerical_selection"]={
        "nx":boundary.nx,"nz":boundary.nz,"duration_s":duration_s,"cfl":cfl,"max_timestep_s":max_timestep_s,
        "conductivity_W_m_K":conductivity_W_m_K,"gravity_m_s2":gravity_m_s2}
    return result
