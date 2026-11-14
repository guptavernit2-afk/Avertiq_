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

function connection(path = ':memory:') {
  const sqlite = new DatabaseSync(path);
  // Exercise the real generated schema, not a second test-only schema.
  for (const file of readdirSync(new URL('../drizzle/', import.meta.url)).filter(f => f.endsWith('.sql')).sort()) sqlite.exec(readFileSync(new URL(`../drizzle/${file}`, import.meta.url), 'utf8'));
  const db: IncidentDatabase = { prepare(sql: string): Statement {
    let values: (string | number)[] = [];
    return { bind(...args) { values = args; return this; }, async first<T>() { return (sqlite.prepare(sql).get(...values) ?? null) as T | null; }, async run() { return { meta: { changes: Number(sqlite.prepare(sql).run(...values).changes) } }; } };
  } };
  return { sqlite, store: new IncidentStore(db) };
}
async function send(api: ReturnType<typeof incidentApi>, method = 'GET', body?: unknown) {
  const response = await api(new Request('http://127.0.0.1:5174/api/incident', { method, ...(body === undefined ? {} : { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }) }));
  return { code: response.status, data: await response.json() as { incident: Incident; assessment: ReturnType<typeof assessmentView>; error?: string } };
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
