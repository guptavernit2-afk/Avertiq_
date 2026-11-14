import { DatabaseSync } from 'node:sqlite';
import { createHash } from 'node:crypto';
import { openSync, closeSync, fsyncSync, writeFileSync, readFileSync, statSync, realpathSync, existsSync } from 'node:fs';
import { resolve, dirname, basename } from 'node:path';
import { validateIncident } from './backup-validation.ts';

const MAX_BYTES=16*1024*1024;
const FORMAT='avertiq-local-incident-backup-v1';
const migration=readFileSync(new URL('../drizzle/0000_fine_mysterio.sql',import.meta.url),'utf8').replace(/\r\n/g,'\n');
const hash=(text:string)=>createHash('sha256').update(text,'utf8').digest('hex');
function check(condition:unknown,message:string): asserts condition { if(!condition) throw new Error(message); }
function outputPath(path:string) {
  const full=resolve(path);
  const parent=realpathSync(dirname(full));
  check(![...full.split(/[\\/]/),...parent.split(/[\\/]/)].some(p=>p.toLowerCase()==='.wrangler'),'Restore/backup output must be outside .wrangler; live database replacement is not supported.');
  const target=resolve(parent,basename(full));
  check(![target,`${target}-wal`,`${target}-shm`,`${target}-journal`].some(existsSync),'Output or SQLite sidecar already exists; choose a fresh path.');
  return target;
}
export function inspectDatabase(path:string) {
  check(statSync(path).isFile(),'Source must be a regular SQLite file.');
  const db=new DatabaseSync(path,{readOnly:true});
  try {
    db.exec('PRAGMA query_only = ON; BEGIN');
    const integrity=db.prepare('PRAGMA integrity_check').all();
    check(integrity.length===1 && Object.values(integrity[0])[0]==='ok','SQLite integrity check failed.');
    const columns=db.prepare('PRAGMA table_info(incidents)').all();
    check(columns.map(c=>`${c.name}:${String(c.type).toUpperCase()}`).join(',')==='id:TEXT,version:INTEGER,payload:TEXT','Unsupported incident table schema.');
    const rows=db.prepare('SELECT id, version, payload FROM incidents').all();
    check(rows.length===1 && rows[0].id==='D-001','Expected exactly one initialized D-001 incident.');
    const payload=rows[0].payload;
    check(typeof payload==='string' && Buffer.byteLength(payload)<=MAX_BYTES/2,'Incident payload exceeds backup limit.');
    const incident=validateIncident(JSON.parse(payload));
    check(rows[0].version===incident.version,'Database version differs from payload version.');
    db.exec('COMMIT');
    return {payload,incident};
  } finally { db.close(); }
}
export function verifyBackup(path:string) {
  check(statSync(path).isFile() && statSync(path).size<=MAX_BYTES,'Backup exceeds size limit or is not a regular file.');
  const backup=JSON.parse(readFileSync(path,'utf8'));
  check(backup?.format===FORMAT && backup.schemaSha256===hash(migration),'Unsupported backup format or database schema version.');
  check(typeof backup.createdAt==='string' && Number.isFinite(Date.parse(backup.createdAt)),'Invalid backup timestamp.');
  check(typeof backup.payload==='string' && backup.sha256===hash(backup.payload),'Backup checksum mismatch.');
  const incident=validateIncident(JSON.parse(backup.payload));
  return {payload:backup.payload as string,incident};
}
export function backupDatabase(source:string,output:string) {
  const target=outputPath(output);
  const {payload,incident}=inspectDatabase(source);
  const contents=JSON.stringify({format:FORMAT,createdAt:new Date().toISOString(),schemaSha256:hash(migration),sha256:hash(payload),payload},null,2)+'\n';
  check(Buffer.byteLength(contents)<=MAX_BYTES,'Serialized backup exceeds size limit.');
  const fd=openSync(target,'wx',0o600);
  try { writeFileSync(fd,contents,'utf8'); fsyncSync(fd); } finally { closeSync(fd); }
  verifyBackup(target);
  return {path:target,version:incident.version,sha256:hash(payload)};
}
export function restoreBackup(source:string,output:string) {
  const {payload,incident}=verifyBackup(source);
  const target=outputPath(output);
  // Exclusive creation prevents accidental replacement, even if another writer
  // creates the destination after outputPath checked it.
  closeSync(openSync(target,'wx',0o600));
  const db=new DatabaseSync(target);
  try {
    db.exec('BEGIN IMMEDIATE');
    db.exec(migration); // Trusted versioned schema, never SQL from the backup.
    db.prepare('INSERT INTO incidents (id,version,payload) VALUES (?,?,?)').run(incident.id,incident.version,payload);
    db.exec('COMMIT');
  } finally { db.close(); }
  check(inspectDatabase(target).payload===payload,'Restored payload differs from backup.');
  return {path:target,version:incident.version,sha256:hash(payload)};
}
