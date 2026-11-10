import test from 'node:test';
import assert from 'node:assert/strict';
import { PRESETS, TRAINING_LABEL, exportRecord, fixtureIsCurrent, handoverHtml, initialWorkspace, loadPreset, restoreWorkspace, type Inputs } from './demo.ts';

test('every unsupported input edit invalidates the prepared assessment', () => {
  for (const key of Object.keys(PRESETS.A) as (keyof Inputs)[]) {
    const w = initialWorkspace(); w.inputs[key] = 'different';
    assert.equal(fixtureIsCurrent(w), false, key);
    const result = exportRecord(w);
    assert.equal(result.assessment.status, 'stale');
    assert.equal(result.assessment.geometry, null);
    assert.equal(result.assessment.hazardDistance, null);
  }
});
test('loading revision B preserves A and makes independent immutable snapshots', () => {
  const a = initialWorkspace(); const b = loadPreset(a,'B');
  b.inputs.windSpeed = '12';
  assert.deepEqual(a.inputs, PRESETS.A);
  assert.deepEqual(b.revisions[0].inputs, PRESETS.A);
  assert.deepEqual(b.revisions[1].inputs, PRESETS.B);
  assert.equal(loadPreset(b,'B').revisions.length, 2);
  assert.equal(loadPreset(b,'B').inputs.windSpeed, '2');
});
test('round-trip persistence retains observations, revisions, edited drafts and reviews', () => {
  const w = loadPreset(initialWorkspace(),'B');
  w.inputs.chemical = 'CNG'; w.reviewedPlaces = ['school'];
  w.observations = [{ id:'o1', time:'T+05', text:'Driver report: leak ongoing.',kind:'Field report',synthetic:true }];
  const restored = restoreWorkspace(JSON.stringify(w));
  assert.deepEqual(restored,w); assert.equal(fixtureIsCurrent(restored!),false);
});
test('corrupt, forged and unsupported stored records cannot qualify an assessment', () => {
  assert.equal(restoreWorkspace('{'),null); assert.equal(restoreWorkspace(null),null);
  const w=initialWorkspace(); w.revisions[0].inputs.windSpeed='200';
  assert.equal(restoreWorkspace(JSON.stringify(w)),null);
  const o=initialWorkspace(); o.observations=[{id:'x',time:'T+05',text:'unlabelled',kind:'Field report',synthetic:false as unknown as true}];
  assert.equal(restoreWorkspace(JSON.stringify(o)),null);
  const forged={...initialWorkspace(),label:'Operationally validated',synthetic:false,assessment:{calculated:true}};
  const restored=restoreWorkspace(JSON.stringify(forged))!;
  assert.equal(exportRecord(restored).label,TRAINING_LABEL);
  assert.equal(exportRecord(restored).synthetic,true);
  assert.equal(exportRecord(restored).assessment.calculated,false);
});
test('valid illustrations carry closed geometry, provenance and no invented physical quantities', () => {
  for (const id of ['A','B'] as const) {
    const r=exportRecord(loadPreset(initialWorkspace(),id));
    const ring=r.assessment.geometry!.coordinates[0];
    assert.deepEqual(ring[0],ring.at(-1));
    assert.equal(r.assessment.threshold,null); assert.equal(r.assessment.calculated,false);
    assert.equal(r.assessment.terrainAffectsPhysics,false);
    assert.match(r.location.source,/not verified accident/);
  }
});
test('handover retains training labels, A/B inputs and safely renders untrusted note text', () => {
  const w=loadPreset(initialWorkspace(),'B');
  w.observations=[{id:'x',time:'T+05',text:'<script>alert("x")</script>',kind:'Field report',synthetic:true}];
  const html=handoverHtml(w,'data:image/png;base64," onerror="alert(1)');
  assert.ok(html.includes(TRAINING_LABEL));
  assert.match(html,/Revision A/); assert.match(html,/Revision B/);
  assert.match(html,/&lt;script&gt;/); assert.doesNotMatch(html,/<script>|onerror=/);
  assert.match(html,/SIMULATED/); assert.match(html,/authority review/);
});
test('outdated handover excludes even a previously captured map image', () => {
  const w=initialWorkspace(); w.inputs.chemical='LPG';
  const html=handoverHtml(w,'data:image/png;base64,AAAA');
  assert.match(html,/OUTDATED/); assert.doesNotMatch(html,/<img/);
});
