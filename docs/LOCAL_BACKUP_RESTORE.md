# Local incident backup and recovery drill

This tool protects the saved D-001 training workflow: inputs, immutable revisions, synthetic observations, review state, jobs, retry identity and events. It is a **logical incident backup**, not a raw copy of all D1 tables. Browser drafts, images, application code, migrations metadata, other database tables and credentials are excluded. Dashboard JSON handovers are not restore backups.

Use Node 24+ from `website`. Commands do not contact a cloud service or start a browser. A backup is read from an explicitly selected database through a read-only SQLite transaction, including committed WAL state. Do not copy only the main SQLite file while a WAL-backed application is running.

## Inspect and back up

List candidate local database files without guessing a generated filename:

```powershell
rg --files --hidden --no-ignore .wrangler/state | rg '\.sqlite$'
```

Inspect the selected path. The command requires the known incident schema, SQLite integrity, exactly one D-001 record, matching row/payload versions and consistent history. It prints counts, not the incident contents. If multiple candidates exist, inspect each and choose the intended saved incident; the tool never auto-selects a file.

```powershell
npm run db:inspect -- "C:/absolute/path/to/source.sqlite"
New-Item -ItemType Directory -Force outputs/backups
npm run db:backup -- "C:/absolute/path/to/source.sqlite" "outputs/backups/d001-01.avertiq-backup.json"
npm run db:verify -- "outputs/backups/d001-01.avertiq-backup.json"
```

Use a fresh backup filename each time. Verification checks format, the versioned database-schema fingerprint, SHA-256 of the exact saved payload, and incident invariants. The fingerprint normalizes SQL line endings. The checksum detects corruption; it is not a signature or proof that a file came from a trusted person. Backups are plaintext and contain the saved notes; use only your own trusted local backup. Files are ignored by Git and are not uploaded by these commands.

## Restore into a fresh database

```powershell
New-Item -ItemType Directory -Force outputs/recovery
npm run db:restore -- "outputs/backups/d001-01.avertiq-backup.json" "outputs/recovery/d001-restored.sqlite"
npm run db:inspect -- "outputs/recovery/d001-restored.sqlite"
```

Restore validates before creating the target, applies only the repository's trusted schema, inserts the exact original payload, then reopens and verifies SQLite integrity and payload equality. It refuses existing destination files, SQLite sidecars and any output inside `.wrangler` (including resolved parent paths). It does not erase history, overwrite the running database, execute backup-supplied SQL, auto-import a handover, or switch the dashboard to the restored file.

This milestone provides a verified recovery artifact. Promotion into a live Wrangler database is a separate, supervised operation requiring a stopped server and an explicit destination choice; no automatic promotion command is provided. Original and backup files stay intact. If a disk/write failure occurs after creating a new destination, the command exits nonzero and may leave a partial file: do not use it; choose a new destination after fixing the failure. Only a successful verified command establishes a usable artifact.

Queued/running jobs are preserved exactly at backup time. When a restored record is subsequently used through the incident API, the normal 60-second lease recovery marks expired work failed; restore itself does not invent completed results or rewrite timestamps.

## Verification performed

`npm test` includes disposable SQLite round trips, committed WAL reads with unchanged source bytes, exact history and export equality, retry deduplication after restore, new saved revisions/jobs, expired-job recovery, malformed/checksum/schema/domain rejection, output/sidecar/live-path protections, missing/corrupt database errors and CLI exit behaviour. All test files live in fresh OS temporary directories and are cleaned up. No user's live database is used by the tests. Typecheck and build are also required.

The SQLite interface uses Node's [documented read-only connection option](https://nodejs.org/api/sqlite.html). Backup schema v1 supports the current single-incident schema only; future schema changes require an explicit compatible restore route.
