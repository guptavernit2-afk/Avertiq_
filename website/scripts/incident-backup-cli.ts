import { backupDatabase, restoreBackup, verifyBackup, inspectDatabase } from './incident-backup.ts';

const [command,source,output,...extra]=process.argv.slice(2);
try {
  if(extra.length || !source || !['backup','verify','restore','inspect'].includes(command) || (command==='verify'||command==='inspect' ? !!output : !output)) throw new Error('Usage: npm run db:inspect -- <source.sqlite> | npm run db:backup -- <source.sqlite> <new.avertiq-backup.json> | npm run db:verify -- <backup> | npm run db:restore -- <backup> <new.sqlite>');
  let result;
  if(command==='backup') result=backupDatabase(source,output);
  else if(command==='restore') result=restoreBackup(source,output);
  else {
    const {incident}=command==='inspect'?inspectDatabase(source):verifyBackup(source);
    result={incident:incident.id,version:incident.version,revisions:incident.revisions.length,jobs:incident.jobs.length,events:incident.events.length};
  }
  console.log(JSON.stringify({status:'verified',command,...result}));
} catch(error) {
  console.error(`Local backup/restore failed: ${error instanceof Error ? error.message : String(error)}`);
  process.exitCode=1;
}
