"""Fabricated records exist ONLY in temporary test directories; no model is run."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from propylene import NAMES, ROOT, registered_case, preparation_report, template, inspect_run, compare_runs
from qualify import read_json, case_hash

class PropyleneTests(unittest.TestCase):
    def observed(self, folder, name='baseline'):
        case = registered_case(name)
        record = template(case)
        path = Path(folder) / 'SYNTHETIC-TEST-ONLY.txt'
        path.write_text('Fabricated validator fixture; not physical evidence', encoding='utf-8')
        record.update(run_completed=True, synthetic_test_data=False, run_at_utc='2026-11-14T00:00:00Z',
                      observed_inputs=copy.deepcopy(case['model_inputs']), dispersion_method='Gaussian', warnings=[],
                      operator_notes='Synthetic test fixture only', mapping_review='Synthetic test; applicability unresolved',
                      evidence_files=[{'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}])
        record['engine']['executable_sha256'] = read_json(ROOT/'engine-manifest.json')['runtime_files']['ALOHA.EXE']
        record['source_summary'] = {'duration_s':600, 'airborne_mass_kg':case['source']['rate_kg_s']*600}
        record['basis'].update(receptor_height_m=0, statistic='synthetic test statistic', averaging_description='synthetic test average', time_window_description='synthetic test window', display_mode=case['model_inputs']['display_mode'])
        for row in record['receptors']: row['value_ppm']=1
        for row in record['contours']: row['unavailable_reason']='Synthetic test: no numeric contour'
        return record

    def test_four_frozen_cases_only_declared_changes(self):
        report=preparation_report()
        self.assertEqual([c['arithmetic_only']['airborne_mass_kg'] for c in report['cases']],[60,30,120,60])
        self.assertFalse(report['model_calculation_performed'])
        baseline=registered_case('baseline')
        for name in NAMES:
            case=registered_case(name)
            self.assertTrue(case['mapping_pending'])
            self.assertEqual(case['model_inputs']['latitude_deg'],18+45.8/60)
            self.assertNotIn('source_temperature_K',case['model_inputs'])
            differences={k for k in baseline['model_inputs'] if baseline['model_inputs'][k]!=case['model_inputs'][k]}
            self.assertEqual(differences, set() if name=='baseline' else {'wind_m_s'} if name=='wind-higher' else {'rate_kg_s'})
            self.assertTrue(case['gates']['reference_reproduction_passed'])

    def test_all_templates_are_unrun_and_rejected(self):
        for name in NAMES:
            case=registered_case(name)
            saved=read_json(ROOT/'templates'/f'propylene-{name}-unrun.json')
            self.assertEqual(saved,template(case))
            with self.assertRaises(ValueError): inspect_run(case,saved,ROOT)
            self.assertTrue(all(r['value_ppm'] is None for r in saved['receptors']))

    def test_record_checks_never_grant_qualification(self):
        with tempfile.TemporaryDirectory() as folder:
            result=inspect_run(registered_case('baseline'),self.observed(folder),Path(folder))
            self.assertTrue(result['record_checks_passed'])
            self.assertFalse(result['propylene_qualified'])
            self.assertFalse(result['field_validated'])
            self.assertFalse(result['dashboard_adapter_enabled'])
            self.assertTrue(result['open_mapping_gates'])
            self.assertFalse(result['source_treatment_review']['source_state_equivalence_established'])
            self.assertIsNone(result['source_treatment_review']['effective_model_source_state']['temperature_K'])

    def test_identity_units_missing_metadata_and_source_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            original=self.observed(folder)
            edits=[('case_sha256','wrong'),('run_completed',False),('synthetic_test_data',True),('run_at_utc','2026-11-14T00:00:00'),('warnings',None),('mapping_review',''),('evidence_files',[]),('dispersion_method','assumed')]
            variants=[]
            for key,value in edits:
                r=copy.deepcopy(original);r[key]=value;variants.append(r)
            for section,key,value in [('engine','version','5.4.4'),('observed_inputs','chemical_CAS','74-98-6'),('observed_inputs','duration_min',600),('basis','concentration_unit','mg/m3'),('basis','receptor_height_m',True),('basis','averaging_description',''),('source_summary','airborne_mass_kg',600),('source_summary','duration_s',True)]:
                r=copy.deepcopy(original);r[section][key]=value;variants.append(r)
            for r in variants:
                with self.assertRaises(ValueError):inspect_run(registered_case('baseline'),r,Path(folder))

    def test_points_censoring_duplicates_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            for value in [-1,float('nan'),float('inf'),True,1000001,None]:
                r=self.observed(folder);r['receptors'][0]['value_ppm']=value
                with self.assertRaises(ValueError):inspect_run(registered_case('baseline'),r,Path(folder))
            r=self.observed(folder);r['receptors'][0]['value_ppm']=None;r['receptors'][0]['unavailable_reason']='Model output not available at this receptor'
            self.assertIsNone(inspect_run(registered_case('baseline'),r,Path(folder))['receptors'][0]['value_ppm'])
            r=self.observed(folder);r['receptors'][1]=copy.deepcopy(r['receptors'][0])
            with self.assertRaises(ValueError):inspect_run(registered_case('baseline'),r,Path(folder))
            r=self.observed(folder);r['contours'].pop()
            with self.assertRaises(ValueError):inspect_run(registered_case('baseline'),r,Path(folder))

    def test_raw_evidence_hash_and_path_bounds(self):
        with tempfile.TemporaryDirectory() as folder:
            r=self.observed(folder);r['evidence_files'][0]['sha256']='wrong'
            with self.assertRaises(ValueError):inspect_run(registered_case('baseline'),r,Path(folder))
            r=self.observed(folder);r['evidence_files'][0]['path']='../outside.txt'
            with self.assertRaises(ValueError):inspect_run(registered_case('baseline'),r,Path(folder))

    def test_comparison_requires_matching_method_and_basis_and_handles_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in NAMES:
                r=self.observed(folder,name)
                r['receptors'][0]['value_ppm']=0
                if name=='rate-half':r['dispersion_method']='Heavy Gas'
                if name=='rate-double':r['basis']['averaging_description']='Different synthetic basis'
                (Path(folder)/f'{name}.json').write_text(json.dumps(r),encoding='utf-8')
            result=compare_runs(Path(folder))
            self.assertEqual([c['comparable_basis'] for c in result['comparisons']],[False,False,True])
            self.assertEqual(result['comparisons'][0]['receptor_changes'],[])
            self.assertIsNone(result['comparisons'][2]['receptor_changes'][0]['ratio'])
            self.assertFalse(result['propylene_qualified'])

    def test_cli_refuses_overwrite_and_does_not_write_rejected_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'report.json'
            command=[sys.executable,str(ROOT/'propylene.py'),'prepare-check','--output',str(output)]
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            first=output.read_bytes()
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            self.assertEqual(output.read_bytes(),first)
            source=Path(folder)/'unrun.json';source.write_text(json.dumps(template(registered_case('baseline'))))
            rejected=Path(folder)/'rejected.json'
            call=[sys.executable,str(ROOT/'propylene.py'),'inspect-run','--observed',str(source),'--output',str(rejected)]
            self.assertNotEqual(subprocess.run(call,capture_output=True).returncode,0)
            self.assertFalse(rejected.exists())
            for name in NAMES:
                (Path(folder)/f'{name}.json').write_text(json.dumps(self.observed(folder,name)),encoding='utf-8')
            comparison=Path(folder)/'comparison.json'
            command=[sys.executable,str(ROOT/'propylene.py'),'compare-runs','--runs-dir',folder,'--output',str(comparison)]
            result=subprocess.run(command,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(read_json(comparison)['dashboard_adapter_enabled'])

if __name__=='__main__':unittest.main()
