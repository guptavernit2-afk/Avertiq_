import copy
import unittest
from propylene import registered_case, NAMES
from source_state import screen_source_state
from qualify import ROOT, read_json

class SourceStateTests(unittest.TestCase):
    def test_all_prepared_cases_support_only_the_declared_equilibrium_state(self):
        for name in NAMES:
            result=screen_source_state(registered_case(name))
            self.assertTrue(result['declared_equilibrium_gas_consistent'])
            self.assertFalse(result['antoine_temperature_in_published_range'])
            for flag in ['vapor_pressure_calculated','actual_release_phase_known','actual_release_temperature_known','aloha_internal_source_state_verified','model_calculation_performed','propylene_qualified','field_validated','dashboard_adapter_enabled']:
                self.assertFalse(result[flag],flag)

    def test_pressure_mixtures_droplets_and_other_chemicals_remain_unsupported(self):
        for section,key,value in [('source','pressure_Pa',101324.0),('source','pressure_Pa',1000000),('source','droplets',True),('source','phase','two_phase'),('chemical','CAS','74-98-6'),('chemical','composition_mole_fraction',.9)]:
            case=copy.deepcopy(registered_case('baseline'));case[section][key]=value
            self.assertFalse(screen_source_state(case)['declared_equilibrium_gas_consistent'])

    def test_boiling_and_critical_screening_boundaries_are_not_accepted(self):
        e=read_json(ROOT/'propylene-state-evidence.json')
        for temperature in [100,225.6,e['normal_boiling_temperature_K']+e['reported_boiling_spread_K'],e['critical_temperature_K']-e['reported_critical_spread_K'],400]:
            case=copy.deepcopy(registered_case('baseline'));case['source']['temperature_K']=temperature
            result=screen_source_state(case)
            self.assertFalse(result['declared_equilibrium_gas_consistent'])
            self.assertFalse(result['vapor_pressure_calculated'])

    def test_invalid_numeric_assumptions_are_rejected(self):
        for key in ['temperature_K','pressure_Pa']:
            for value in [None,True,0,-1,'298.15',float('nan'),float('inf')]:
                case=copy.deepcopy(registered_case('baseline'));case['source'][key]=value
                with self.assertRaises(ValueError):screen_source_state(case)
        case=copy.deepcopy(registered_case('baseline'));case['chemical']['composition_mole_fraction']=True
        with self.assertRaises(ValueError):screen_source_state(case)

if __name__=='__main__':unittest.main()
