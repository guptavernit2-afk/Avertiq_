import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { IncidentStore, type IncidentDatabase, type Statement } from './incident-store.ts';
import { incidentApi } from './incident-api.ts';
import { assessmentView, queueAssessment, transitionJob, type Incident } from './incident.ts';
import { PRESETS, exportRecord, handoverHtml, loadPreset } from './demo.ts';

function connection(path = ':memory:', fault?: (sql: string, phase: 'before' | 'after') => void) {
  const sqlite = new DatabaseSync(path);
  // Exercise the real generated schema, not a second test-only schema.
  for (const file of readdirSync(new URL('../drizzle/', import.meta.url)).filter(f => f.endsWith('.sql')).sort()) sqlite.exec(readFileSync(new URL(`../drizzle/${file}`, import.meta.url), 'utf8'));
  const db: IncidentDatabase = { prepare(sql: string): Statement {
    let values: (string | number)[] = [];
    return { bind(...args) { values = args; return this; }, async first<T>() { return (sqlite.prepare(sql).get(...values) ?? null) as T | null; }, async run() { fault?.(sql,'before'); const changes=Number(sqlite.prepare(sql).run(...values).changes); fault?.(sql,'after'); return { meta: { changes } }; } };
  } };
  return { sqlite, store: new IncidentStore(db) };
}
async function send(api: ReturnType<typeof incidentApi>, method = 'GET', body?: unknown) {
  const response = await api(new Request('http://127.0.0.1:5174/api/incident', { method, ...(body === undefined ? {} : { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }) }));
  return { code: response.status, data: await response.json() as { incident: Incident; assessment: ReturnType<typeof assessmentView>; requestJobId?: string; error?: string } };
}

test('saved inputs and jobs survive a fresh database connection; A stays immutable after B', async () => {
  const folder = mkdtempSync(join(tmpdir(), 'avertiq-incident-')); const file = join(folder, 'incident.sqlite');
  let c = connection(file);
  try {
    const api = incidentApi(c.store);
    const first = (await send(api)).data.incident;
    const a = (await send(api,'POST',{expectedVersion:first.version})).data;
    assert.equal(a.assessment.status,'completed'); assert.equal(a.assessment.calculated,false);
    const bWorkspace = { ...a.incident.workspace, inputs: { ...PRESETS.B } };
    bWorkspace.observations.push({id:'note',kind:'Weather report',time:'T+05',text:'Synthetic wind update',synthetic:true});
    const saved = await send(api,'PUT',{expectedVersion:a.incident.version,workspace:bWorkspace});
    assert.equal(saved.data.assessment.status,'stale'); assert.equal(saved.data.assessment.geometry,null);
    const b = await send(api,'POST',{expectedVersion:saved.data.incident.version});
    assert.equal(b.data.assessment.job?.fixture,'B');
    assert.equal(b.data.incident.workspace.activeRevision,'B');
    assert.deepEqual(b.data.incident.revisions[0].inputs,PRESETS.A);
    assert.equal(b.data.incident.jobs[0].revisionId,'R001');
    c.sqlite.close();
    // Reopen without replaying migrations, like restarting the local server.
    const reopened = new DatabaseSync(file);
    const row = reopened.prepare('SELECT payload FROM incidents WHERE id = ?').get('D-001') as {payload:string};
    const persisted = JSON.parse(row.payload) as Incident;
    assert.deepEqual(persisted,b.data.incident);
    assert.equal(persisted.workspace.observations[0].synthetic,true);
    assert.ok(persisted.events.some(e=>e.type==='assessment-running'));
    reopened.close();
  } finally { if (c.sqlite.isOpen) c.sqlite.close(); rmSync(folder,{recursive:true,force:true}); }
});

test('concurrent stale writes and stale assessment requests cannot overwrite saved history', async () => {
  const { sqlite, store } = connection();
  try {
    const api=incidentApi(store); const initial=(await send(api)).data.incident;
    const edits=loadPreset(initial.workspace,'B');
    const results=await Promise.all([send(api,'PUT',{expectedVersion:initial.version,workspace:edits}),send(api,'PUT',{expectedVersion:initial.version,workspace:initial.workspace})]);
    assert.deepEqual(results.map(r=>r.code).sort(),[200,409]);
    assert.equal((await send(api,'POST',{expectedVersion:initial.version})).code,409);
    assert.equal((await store.read()).events.length,2);
  } finally { sqlite.close(); }
});

test('missing, invalid, unsupported chemical and storage inputs produce reasons and no geometry', async () => {
  const {sqlite,store}=connection();
  try {
    const api=incidentApi(store); let state=(await send(api)).data.incident;
    for (const changes of [{windSpeed:''},{releaseRate:'-1'},{temperature:'-273.15'},{chemical:'CNG'},{chemical:'LPG'},{asset:'Fixed storage vessel'},{releaseRate:'0.2'}]) {
      const workspace={...state.workspace,inputs:{...PRESETS.A,...changes}};
      const saved=await send(api,'PUT',{expectedVersion:state.version,workspace}); assert.equal(saved.code,200);
      const result=await send(api,'POST',{expectedVersion:saved.data.incident.version});
      assert.equal(result.code,200); assert.equal(result.data.assessment.status,'unsupported');
      assert.equal(result.data.assessment.geometry,null); assert.equal(result.data.assessment.calculated,false);
      assert.ok(result.data.assessment.reason.length>25); state=result.data.incident;
    }
  } finally { sqlite.close(); }
});

test('request validation rejects forged labels, malformed JSON, cross-origin and nonlocal calls', async () => {
  const {sqlite,store}=connection();
  try {
    const api=incidentApi(store); const state=(await send(api)).data.incident;
    const forged=structuredClone(state.workspace); forged.observations=[{id:'x',text:'Real',kind:'Field report',time:'T+01',synthetic:false as unknown as true}];
    assert.equal((await send(api,'PUT',{expectedVersion:state.version,workspace:forged})).code,400);
    assert.equal((await api(new Request('http://localhost/api/incident',{method:'POST',headers:{'Content-Type':'application/json'},body:'{'}))).status,400);
    assert.equal((await api(new Request('http://localhost/api/incident',{headers:{Origin:'https://other.example'}}))).status,403);
    assert.equal((await api(new Request('https://example.com/api/incident'))).status,403);
    assert.equal((await send(api,'PUT',{expectedVersion:state.version,workspace:{...state.workspace,assessment:{calculated:true}}})).data.incident.jobs.length,0);
  } finally { sqlite.close(); }
});

test('interrupted jobs recover as failed with no illustration, and can be retried', async () => {
  const {sqlite,store}=connection();
  try {
    const old=new Date(Date.now()-120000).toISOString();
    let state=await store.initialize(old);
    state=await store.write(queueAssessment(state,'interrupted',old),state.version);
    state=await store.write(transitionJob(state,'interrupted','running',old),state.version);
    const api=incidentApi(store); const recovered=await send(api);
    assert.equal(recovered.data.assessment.status,'failed'); assert.equal(recovered.data.assessment.geometry,null);
    const retry=await send(api,'POST',{expectedVersion:recovered.data.incident.version});
    assert.equal(retry.data.assessment.status,'completed'); assert.equal(retry.data.incident.jobs[0].status,'failed');
  } finally { sqlite.close(); }
});

test('database errors stay unavailable; exports cannot leak a matching preset without a completed job', async () => {
  const {sqlite,store}=connection();
  try {
    const state=await store.initialize(new Date().toISOString());
    assert.equal(exportRecord(state.workspace,false).assessment.geometry,null);
    assert.doesNotMatch(handoverHtml(state.workspace,'data:image/png;base64,AAAA',false),/<img/);
    assert.equal(assessmentView(state).status,'not-run');
    sqlite.exec('DROP TABLE incidents');
    const unavailable=await send(incidentApi(store)); assert.equal(unavailable.code,503);
    assert.ok(unavailable.data.error); assert.equal(unavailable.data.incident,undefined);
  } finally { sqlite.close(); }
});

test('invalid envelopes and media types do not initialize or recover state', async () => {
  const {sqlite,store}=connection();
  try {
    const api=incidentApi(store);
    for (const body of ['null','[]','42','"text"','{','{}','{"expectedVersion":"1"}']) {
      assert.equal((await api(new Request('http://localhost/api/incident',{method:'POST',headers:{'Content-Type':'application/json'},body}))).status,400);
    }
    for (const type of ['text/plain','application/jsonp','text/application/json']) {
      assert.equal((await api(new Request('http://localhost/api/incident',{method:'POST',headers:{'Content-Type':type},body:'{"expectedVersion":1}'}))).status,415);
    }
    assert.equal((sqlite.prepare('SELECT count(*) AS n FROM incidents').get() as {n:number}).n,0);
    const old=new Date(Date.now()-120000).toISOString();
    let state=await store.initialize(old);
    state=await store.write(queueAssessment(state,'pending',old),state.version);
    await api(new Request('http://localhost/api/incident',{method:'POST',headers:{'Content-Type':'application/json'},body:'{'}));
    assert.deepEqual(await store.read(),state);
  } finally { sqlite.close(); }
});

test('request limit counts UTF-8 bytes and valid JSON parameters remain accepted', async () => {
  const {sqlite,store}=connection();
  try {
    const api=incidentApi(store);
    const oversized=JSON.stringify({expectedVersion:1,padding:'\u0905'.repeat(90000)});
    assert.ok(oversized.length<256000);
    assert.equal((await api(new Request('http://localhost/api/incident',{method:'POST',headers:{'Content-Type':'application/json'},body:oversized}))).status,413);
    assert.equal((sqlite.prepare('SELECT count(*) AS n FROM incidents').get() as {n:number}).n,0);
    assert.equal((await api(new Request('http://localhost/api/incident',{method:'POST',headers:{'Content-Type':'Application/JSON; charset=utf-8'},body:'{"expectedVersion":1}'}))).status,200);
  } finally { sqlite.close(); }
});


test('lost-response retries reuse persisted jobs and preserve newer input revisions', async () => {
  const {sqlite,store}=connection();
  try {
    let api=incidentApi(store);
    const initial=(await send(api)).data.incident;
    const first=await send(api,'POST',{expectedVersion:initial.version});
    api=incidentApi(store); // fresh handler, no process-local retry cache
    const retry=await send(api,'POST',{expectedVersion:initial.version});
    assert.equal(retry.code,200);
    assert.deepEqual(retry.data,first.data);
    const saved=await send(api,'PUT',{expectedVersion:first.data.incident.version,workspace:loadPreset(first.data.incident.workspace,'B')});
    const later=await send(api,'POST',{expectedVersion:initial.version});
    assert.equal(later.code,200);
    assert.equal(later.data.requestJobId,first.data.requestJobId);
    assert.deepEqual(later.data.incident,saved.data.incident);
    assert.equal(later.data.assessment.status,'stale');
    assert.equal(later.data.assessment.geometry,null);
    const newRun=await send(api,'POST',{expectedVersion:saved.data.incident.version});
    assert.equal(newRun.data.incident.jobs.length,2);
    assert.notEqual(newRun.data.requestJobId,first.data.requestJobId);
  } finally { sqlite.close(); }
});

test('concurrent duplicate assessment requests run exactly one job', async () => {
  const {sqlite,store}=connection();
  try {
    const api=incidentApi(store); const initial=(await send(api)).data.incident;
    const results=await Promise.all(Array.from({length:8},()=>send(incidentApi(store),'POST',{expectedVersion:initial.version})));
    assert.ok(results.every(r=>r.code===200));
    assert.equal(new Set(results.map(r=>r.data.requestJobId)).size,1);
    const state=await store.read();
    assert.equal(state.jobs.length,1);
    assert.equal(state.jobs[0].status,'completed');
    assert.deepEqual(state.events.map(e=>e.type),['created','assessment-queued','assessment-running','assessment-completed']);
    assert.equal(state.revisions.length,1);
    assert.equal(state.version,4);
  } finally { sqlite.close(); }
});

test('unsupported and failed assessment retries cannot start replacement jobs', async () => {
  const {sqlite,store}=connection();
  try {
    const api=incidentApi(store); const initial=(await send(api)).data.incident;
    const saved=await send(api,'PUT',{expectedVersion:initial.version,workspace:{...initial.workspace,inputs:{...PRESETS.A,chemical:'CNG'}}});
    const unsupported=await send(api,'POST',{expectedVersion:saved.data.incident.version});
    const retry=await send(api,'POST',{expectedVersion:saved.data.incident.version});
    assert.deepEqual(retry.data,unsupported.data);
    let state=await store.read(); const requestVersion=state.version;
    const old=new Date(Date.now()-120000).toISOString();
    state=await store.write(queueAssessment(state,'interrupted-retry',old),state.version);
    const failed=await send(api,'POST',{expectedVersion:requestVersion});
    assert.equal(failed.code,200);
    assert.equal(failed.data.requestJobId,'interrupted-retry');
    assert.equal(failed.data.assessment.status,'failed');
    assert.equal(failed.data.assessment.geometry,null);
    const again=await send(api,'POST',{expectedVersion:requestVersion});
    assert.deepEqual(again.data,failed.data);
    assert.equal(again.data.incident.jobs.length,2);
  } finally { sqlite.close(); }
});

test('legacy jobs without request versions retain conflict protection', async () => {
  const {sqlite,store}=connection();
  try {
    const api=incidentApi(store); const initial=(await send(api)).data.incident;
    const first=await send(api,'POST',{expectedVersion:initial.version});
    const legacy=structuredClone(first.data.incident);
    delete legacy.jobs[0].requestedVersion;
    await store.write(legacy,legacy.version);
    assert.equal((await send(api,'POST',{expectedVersion:initial.version})).code,409);
    assert.equal((await store.read()).jobs.length,1);
  } finally { sqlite.close(); }
});


test('lease boundary uses the supplied clock and concurrent recovery records one failure', async () => {
  for (const status of ['queued','running'] as const) {
    const {sqlite,store}=connection();
    try {
      const start='2026-11-14T00:00:00.000Z';
      let state=await store.initialize(start);
      state=await store.write(queueAssessment(state,'expired',start),state.version);
      if (status==='running') state=await store.write(transitionJob(state,'expired','running',start),state.version);
      const fresh=await send(incidentApi(store,()=> '2026-11-14T00:00:59.999Z'));
      assert.equal(fresh.data.assessment.status,status);
      const results=await Promise.all(Array.from({length:6},()=>send(incidentApi(store,()=> '2026-11-14T00:01:00.000Z'))));
      assert.ok(results.every(r=>r.code===200 && r.data.assessment.status==='failed'));
      const saved=await store.read();
      assert.equal(saved.events.filter(e=>e.type==='assessment-failed').length,1);
      assert.equal(saved.version,state.version+1);
      assert.equal(assessmentView(saved).geometry,null);
    } finally { sqlite.close(); }
  }
});

test('write failures before or after commit preserve truthful job state and retry identity', async () => {
  for (const writeNumber of [1,2,3]) for (const phase of ['before','after'] as const) {
    let writes=0; let injected=false;
    const {sqlite,store}=connection(':memory:',(sql,at)=>{
      if (!sql.startsWith('UPDATE')) return;
      if (at==='before') writes++;
      if (!injected && writes===writeNumber && at===phase) { injected=true; throw new Error('Injected storage failure'); }
    });
    try {
      const api=incidentApi(store);
      const initial=(await send(api)).data.incident;
      const result=await send(api,'POST',{expectedVersion:initial.version});
      assert.ok(injected);
      if (writeNumber===1) assert.equal(result.code,503);
      else assert.equal(result.code,200);
      const persisted=await store.read();
      if (writeNumber===1 && phase==='before') assert.equal(persisted.jobs.length,0);
      else {
        assert.equal(persisted.jobs.length,1);
        const expected=writeNumber===1 ? 'queued' : writeNumber===3 && phase==='after' ? 'completed' : 'failed';
        assert.equal(persisted.jobs[0].status,expected);
        assert.equal(persisted.events.filter(e=>e.type==='assessment-failed').length,expected==='failed'?1:0);
        const retry=await send(api,'POST',{expectedVersion:initial.version});
        assert.equal(retry.code,200);
        assert.equal(retry.data.incident.jobs.length,1);
        assert.equal(retry.data.assessment.status,expected);
        if (expected!=='completed') assert.equal(retry.data.assessment.geometry,null);
      }
    } finally { sqlite.close(); }
  }
});

test('persistent write outage returns unavailable and later recovery retains one job', async () => {
  let outage=false;
  const {sqlite,store}=connection(':memory:',(sql,phase)=>{if(outage && sql.startsWith('UPDATE') && phase==='before') throw new Error('Database offline');});
  try {
    const old='2026-11-14T00:00:00.000Z';
    let state=await store.initialize(old);
    state=await store.write(queueAssessment(state,'outage',old),state.version);
    state=await store.write(transitionJob(state,'outage','running',old),state.version);
    outage=true;
    const api=incidentApi(store,()=> '2026-11-14T00:02:00.000Z');
    const unavailable=await send(api);
    assert.equal(unavailable.code,503); assert.equal(unavailable.data.incident,undefined);
    assert.deepEqual(await store.read(),state);
    outage=false;
    const recovered=await send(api);
    assert.equal(recovered.code,200);
    assert.equal(recovered.data.assessment.status,'failed');
    assert.equal(recovered.data.assessment.geometry,null);
    assert.equal(recovered.data.incident.jobs.length,1);
    assert.equal(recovered.data.incident.events.filter(e=>e.type==='assessment-failed').length,1);
  } finally { sqlite.close(); }
});

test('outage during assessment and failed cleanup remains unavailable until later recovery', async () => {
  let updates=0; let outage=true;
  const {sqlite,store}=connection(':memory:',(sql,phase)=>{
    if (sql.startsWith('UPDATE') && phase==='before' && ++updates>=3 && outage) throw new Error('Write outage');
  });
  try {
    const start='2026-11-14T00:00:00.000Z';
    const api=incidentApi(store,()=>start);
    const initial=(await send(api)).data.incident;
    const failed=await send(api,'POST',{expectedVersion:initial.version});
    assert.equal(failed.code,503);
    assert.equal(failed.data.incident,undefined);
    const pending=await store.read();
    assert.equal(pending.jobs[0].status,'running');
    assert.equal(pending.events.some(e=>e.type==='assessment-completed'),false);
    outage=false;
    const recovered=await send(incidentApi(store,()=> '2026-11-14T00:02:00.000Z'),'POST',{expectedVersion:initial.version});
    assert.equal(recovered.code,200);
    assert.equal(recovered.data.assessment.status,'failed');
    assert.equal(recovered.data.assessment.geometry,null);
    assert.equal(recovered.data.incident.jobs.length,1);
  } finally { sqlite.close(); }
});

test('recovery conflict preserves a completion that won the database write', async () => {
  const {sqlite,store}=connection();
  try {
    const old='2026-11-14T00:00:00.000Z';
    let state=await store.initialize(old);
    state=await store.write(queueAssessment(state,'completion-race',old),state.version);
    state=await store.write(transitionJob(state,'completion-race','running',old),state.version);
    const write=store.write.bind(store); let raced=false;
    store.write=async(next,expected)=>{
      if (!raced && next.jobs[0].status==='failed') {
        raced=true;
        await write(transitionJob(state,'completion-race','completed',old),expected);
      }
      return write(next,expected);
    };
    const result=await send(incidentApi(store,()=> '2026-11-14T00:02:00.000Z'));
    assert.equal(result.code,200);
    assert.equal(result.data.assessment.status,'completed');
    assert.equal(result.data.incident.events.some(e=>e.type==='assessment-failed'),false);
    assert.equal(result.data.incident.jobs.length,1);
  } finally { sqlite.close(); }
});

test('recovery rechecks the lease when a competing worker starts the queued job', async () => {
  const {sqlite,store}=connection();
  try {
    const old='2026-11-14T00:00:00.000Z'; const now='2026-11-14T00:02:00.000Z';
    let state=await store.initialize(old);
    state=await store.write(queueAssessment(state,'renewed',old),state.version);
    const write=store.write.bind(store); let raced=false;
    store.write=async(next,expected)=>{
      if (!raced && next.jobs[0].status==='failed') {
        raced=true; await write(transitionJob(state,'renewed','running',now),expected);
      }
      return write(next,expected);
    };
    const result=await send(incidentApi(store,()=>now));
    assert.equal(result.code,200);
    assert.equal(result.data.assessment.status,'running');
    assert.equal(result.data.assessment.geometry,null);
    assert.equal(result.data.incident.events.some(e=>e.type==='assessment-failed'),false);
  } finally { sqlite.close(); }
});
import { incidentExport, incidentHandover, matchingMap } from './incident-export.ts';
import { createIncident, saveWorkspace } from './incident.ts';

const exportTime = '2026-11-14T12:00:00.000Z';
function completedExportState() {
  let state=createIncident(exportTime);
  state=queueAssessment(state,'export-job',exportTime);
  state=transitionJob(state,'export-job','running',exportTime);
  return transitionJob(state,'export-job','completed',exportTime);
}

test('exports bind illustrative geometry to immutable revision, job and timestamps', () => {
  const state=completedExportState();
  const record=incidentExport(state.workspace,state,'',exportTime);
  assert.equal(record.assessment.status,'completed');
  assert.ok(record.assessment.geometry);
  assert.equal(record.exportedAt,exportTime);
  assert.equal(record.provenance.savedInputRevisionId,'R001');
  assert.equal(record.provenance.assessmentRevisionId,'R001');
  assert.equal(record.provenance.assessmentJobId,'export-job');
  assert.equal(record.provenance.adapterVersion,'illustrative-fixture-v1');
  assert.equal(record.provenance.jobCreatedAt,exportTime);
  assert.equal(record.provenance.jobUpdatedAt,exportTime);
  assert.equal(record.provenance.units.duration,'minutes');
  assert.equal(record.assessment.calculated,false);
  assert.equal(record.assessment.threshold,null);
  assert.equal(record.assessment.hazardDistance,null);
  record.backendHistory!.revisions[0].inputs.windSpeed='999';
  record.inputs.chemical='CNG';
  assert.equal(state.revisions[0].inputs.windSpeed,'2');
  assert.equal(state.workspace.inputs.chemical,'Propylene');
});

test('JSON and HTML suppress geometry and captured images for every unavailable status', () => {
  const fresh=createIncident(exportTime);
  const queued=queueAssessment(fresh,'pending',exportTime);
  const running=transitionJob(queued,'pending','running',exportTime);
  const failed=transitionJob(running,'pending','failed',exportTime);
  const completed=completedExportState();
  const stale=saveWorkspace(completed,loadPreset(completed.workspace,'B'),exportTime);
  const unsupportedBase=saveWorkspace(fresh,{...fresh.workspace,inputs:{...PRESETS.A,chemical:'CNG'}},exportTime);
  const unsupported=transitionJob(transitionJob(queueAssessment(unsupportedBase,'unsupported',exportTime),'unsupported','running',exportTime),'unsupported','unsupported',exportTime);
  const cases: [Incident|null, typeof fresh.workspace, string, string][] = [
    [null,fresh.workspace,'','unavailable'],[fresh,fresh.workspace,'','not-run'],
    [queued,queued.workspace,'','queued'],[running,running.workspace,'','running'],
    [failed,failed.workspace,'','failed'],[stale,stale.workspace,'','stale'],
    [unsupported,unsupported.workspace,'','unsupported'],
    [completed,loadPreset(completed.workspace,'B'),'','unsaved-inputs'],
    [completed,completed.workspace,'<script>connection failed</script>','unavailable'],
  ];
  for (const [state,workspace,error,status] of cases) {
    const record=incidentExport(workspace,state,error,exportTime);
    assert.equal(record.assessment.status,status);
    assert.equal(record.assessment.geometry,null);
    assert.equal(record.assessment.fixtureId,null);
    const html=incidentHandover(workspace,state,error,{dataUrl:'data:image/png;base64,AAAA',jobId:'export-job',revisionId:'R001'},exportTime);
    assert.ok(html.includes(`${status}:`));
    assert.doesNotMatch(html,/<img|<script>|OUTDATED: inputs differ/);
  }
});

test('unsaved notes are labelled and map captures cannot cross job or revision boundaries', () => {
  const state=completedExportState();
  const draft=structuredClone(state.workspace);
  draft.observations.push({id:'note',kind:'Field report',time:'T+05',text:'<b>synthetic note</b>',synthetic:true});
  const record=incidentExport(draft,state,'',exportTime);
  assert.equal(record.saved,false);
  assert.equal(record.provenance.inputsMatchSavedRevision,true);
  assert.equal(record.assessment.status,'completed');
  const capture={dataUrl:'data:image/png;base64,AAAA',jobId:'export-job',revisionId:'R001'};
  assert.equal(matchingMap(record,capture),capture.dataUrl);
  assert.equal(matchingMap(record,{...capture,jobId:'old-job'}),undefined);
  assert.equal(matchingMap(record,{...capture,revisionId:'R002'}),undefined);
  const html=incidentHandover(draft,state,'',capture,exportTime);
  assert.match(html,/<img/); assert.match(html,/UNSAVED browser draft/);
  assert.match(html,/&lt;b&gt;synthetic note/);
  assert.match(html,/illustrative-fixture-v1/);
  assert.doesNotMatch(incidentHandover(draft,state,'',{...capture,jobId:'old-job'}),/<img/);
});
