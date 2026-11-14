import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { mkdtempSync, readFileSync, writeFileSync, rmSync, mkdirSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { backupDatabase, restoreBackup, verifyBackup, inspectDatabase } from './incident-backup.ts';
import { IncidentStore, type IncidentDatabase, type Statement } from '../lib/incident-store.ts';
import { incidentApi } from '../lib/incident-api.ts';
import { queueAssessment, transitionJob, type Incident } from '../lib/incident.ts';
import { loadPreset } from '../lib/demo.ts';
import { incidentExport } from '../lib/incident-export.ts';

const migration=readFileSync(new URL('../drizzle/0000_fine_mysterio.sql',import.meta.url),'utf8');
const time='2026-11-14T00:00:00.000Z';
function storeFor(db:DatabaseSync) {
  const adapter:IncidentDatabase={prepare(sql:string):Statement {
    let values:(string|number)[]=[];
    return {bind(...v){values=v;return this;},async first<T>(){return (db.prepare(sql).get(...values)??null) as T|null;},async run(){return {meta:{changes:Number(db.prepare(sql).run(...values).changes)}};}};
  }};
  return new IncidentStore(adapter);
}
async function request(store:IncidentStore,method='GET',body?:unknown,now=time) {
  const response=await incidentApi(store,()=>now)(new Request('http://localhost/api/incident',{method,...(body?{headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{})}));
  assert.equal(response.status,200);
  return (await response.json() as {incident:Incident}).incident;
}
async function fixture(folder:string) {
  const path=join(folder,'source.sqlite'); const db=new DatabaseSync(path);
  db.exec(migration); const store=storeFor(db);
  let state=await request(store);
  state=await request(store,'POST',{expectedVersion:state.version});
  const workspace=loadPreset(state.workspace,'B');
  workspace.observations.push({id:'note',text:'Synthetic observation',kind:'Field report',time:'T+05',synthetic:true});
  workspace.reviewedPlaces=['school'];
  state=await request(store,'PUT',{expectedVersion:state.version,workspace});
  state=await request(store,'POST',{expectedVersion:state.version});
  return {path,db,store,state};
}

test('backup restores exact history and supports API retries and new work after reopen',async()=>{
  const folder=mkdtempSync(join(tmpdir(),'avertiq-backup-')); const f=await fixture(folder);
  try {
    // Include committed WAL data without copying SQLite files by hand.
    f.db.exec('PRAGMA journal_mode=WAL; PRAGMA wal_autocheckpoint=0');
    const state=await request(f.store,'PUT',{expectedVersion:f.state.version,workspace:f.state.workspace});
    const before=readFileSync(f.path); const wal=readFileSync(f.path+'-wal');
    const backup=join(folder,'case.avertiq-backup.json'); const restored=join(folder,'restored.sqlite');
    backupDatabase(f.path,backup);
    assert.deepEqual(readFileSync(f.path),before); assert.deepEqual(readFileSync(f.path+'-wal'),wal);
    assert.deepEqual(verifyBackup(backup).incident,state);
    restoreBackup(backup,restored);
    assert.deepEqual(inspectDatabase(restored).incident,state);
    const db=new DatabaseSync(restored);
    try {
      const store=storeFor(db);
      const replay=await request(store,'POST',{expectedVersion:state.jobs[1].requestedVersion});
      assert.deepEqual(replay,state);
      assert.deepEqual(incidentExport(replay.workspace,replay,'',time),incidentExport(state.workspace,state,'',time));
      const edited=await request(store,'PUT',{expectedVersion:state.version,workspace:loadPreset(state.workspace,'A')});
      const run=await request(store,'POST',{expectedVersion:edited.version});
      assert.equal(run.jobs.length,3); assert.equal(run.revisions.length,3);
      assert.deepEqual(run.revisions.slice(0,2),state.revisions);
    } finally { db.close(); }
    assert.deepEqual((await f.store.read()),state);
  } finally { f.db.close(); rmSync(folder,{recursive:true,force:true}); }
});

test('active jobs are preserved in backup and recovered by the normal restored API',async()=>{
  const folder=mkdtempSync(join(tmpdir(),'avertiq-backup-')); const f=await fixture(folder);
  try {
    let state=await f.store.write(queueAssessment(f.state,'interrupted',time),f.state.version);
    state=await f.store.write(transitionJob(state,'interrupted','running',time),state.version);
    const backup=join(folder,'active.avertiq-backup.json'), restored=join(folder,'active.sqlite');
    backupDatabase(f.path,backup); restoreBackup(backup,restored);
    assert.deepEqual(inspectDatabase(restored).incident,state);
    const db=new DatabaseSync(restored);
    try {
      const recovered=await request(storeFor(db),'GET',undefined,'2026-11-14T00:02:00.000Z');
      assert.equal(recovered.jobs.at(-1)!.status,'failed');
      assert.equal(recovered.jobs.length,state.jobs.length);
      assert.equal(incidentExport(recovered.workspace,recovered).assessment.geometry,null);
    } finally { db.close(); }
    assert.equal((await f.store.read()).jobs.at(-1)!.status,'running');
  } finally { f.db.close(); rmSync(folder,{recursive:true,force:true}); }
});

test('checksum, schema and semantic corruption are rejected before creating destinations',async()=>{
  const folder=mkdtempSync(join(tmpdir(),'avertiq-backup-')); const f=await fixture(folder);
  try {
    const backup=join(folder,'good.avertiq-backup.json'); backupDatabase(f.path,backup);
    const original=JSON.parse(readFileSync(backup,'utf8'));
    const variants=[
      {...original,sha256:'0'.repeat(64)}, {...original,format:'future'}, {...original,schemaSha256:'unknown'},
      ...[(s:Incident)=>{s.jobs[0].calculated=true as false;},(s:Incident)=>{s.jobs[0].revisionId='missing';},(s:Incident)=>{s.jobs[0].fixture='B';},(s:Incident)=>{s.currentRevisionId='R001';},(s:Incident)=>{s.events.pop();}].map(change=>{
        const state=JSON.parse(original.payload);change(state);const payload=JSON.stringify(state);
        return {...original,payload,sha256:createHash('sha256').update(payload).digest('hex')};
      }),
    ];
    for(const [i,value] of variants.entries()) {
      const source=join(folder,`bad-${i}.json`),target=join(folder,`bad-${i}.sqlite`);
      writeFileSync(source,JSON.stringify(value)); assert.throws(()=>restoreBackup(source,target)); assert.equal(existsSync(target),false);
    }
    const truncated=join(folder,'truncated.json');writeFileSync(truncated,'{');assert.throws(()=>verifyBackup(truncated));
    const oversized=join(folder,'large.json');writeFileSync(oversized,Buffer.alloc(16*1024*1024+1));assert.throws(()=>verifyBackup(oversized),/size limit/);
  } finally { f.db.close(); rmSync(folder,{recursive:true,force:true}); }
});

test('overwrite, sidecar and live directory protections preserve existing files',async()=>{
  const folder=mkdtempSync(join(tmpdir(),'avertiq-backup-')); const f=await fixture(folder);
  try {
    const backup=join(folder,'good.avertiq-backup.json');backupDatabase(f.path,backup);
    const original=readFileSync(backup); const source=readFileSync(f.path);
    assert.throws(()=>backupDatabase(f.path,backup),/already exists/);
    assert.throws(()=>restoreBackup(backup,f.path),/already exists/);
    assert.deepEqual(readFileSync(backup),original);assert.deepEqual(readFileSync(f.path),source);
    const target=join(folder,'sidecar.sqlite');writeFileSync(target+'-wal','do not replace');
    assert.throws(()=>restoreBackup(backup,target),/already exists/);assert.equal(existsSync(target),false);
    const live=join(folder,'.wrangler');mkdirSync(live);
    assert.throws(()=>restoreBackup(backup,join(live,'new.sqlite')),/outside .wrangler/);
    assert.throws(()=>backupDatabase(join(folder,'missing.sqlite'),join(folder,'missing.json')));
    assert.equal(existsSync(join(folder,'missing.sqlite')),false);
  } finally { f.db.close(); rmSync(folder,{recursive:true,force:true}); }
});

test('invalid SQLite, wrong schemas and inconsistent row versions fail backup',async()=>{
  const folder=mkdtempSync(join(tmpdir(),'avertiq-backup-')); const f=await fixture(folder);
  try {
    const bad=join(folder,'corrupt.sqlite');writeFileSync(bad,'not sqlite');assert.throws(()=>backupDatabase(bad,join(folder,'bad.json')));
    const empty=join(folder,'empty.sqlite');const db=new DatabaseSync(empty);db.exec('CREATE TABLE other (id TEXT)');db.close();
    assert.throws(()=>backupDatabase(empty,join(folder,'empty.json')),/schema/);
    f.db.exec('UPDATE incidents SET version=999');assert.throws(()=>backupDatabase(f.path,join(folder,'mismatch.json')),/version/);
  } finally { f.db.close(); rmSync(folder,{recursive:true,force:true}); }
});

test('CLI backup verify restore works and invalid calls exit nonzero',async()=>{
  const folder=mkdtempSync(join(tmpdir(),'avertiq-backup-')); const f=await fixture(folder);
  try {
    const cli=fileURLToPath(new URL('./incident-backup-cli.ts',import.meta.url));
    const backup=join(folder,'cli.avertiq-backup.json'), restored=join(folder,'cli.sqlite');
    for(const args of [['inspect',f.path],['backup',f.path,backup],['verify',backup],['restore',backup,restored],['inspect',restored]]) {
      const run=spawnSync(process.execPath,[cli,...args],{encoding:'utf8',windowsHide:true});
      assert.equal(run.status,0,run.stderr);assert.equal(JSON.parse(run.stdout).status,'verified');
    }
    for(const args of [[],['verify',backup,'extra'],['restore',backup,restored]]) assert.equal(spawnSync(process.execPath,[cli,...args],{windowsHide:true}).status,1);
    assert.deepEqual(inspectDatabase(restored).incident,f.state);
  } finally { f.db.close(); rmSync(folder,{recursive:true,force:true}); }
});
