# First local incident backend

Implemented 11 November 2026 for D-001 only. This is a local training workflow with prepared illustrative results, not a physics or emergency-response service.

## What now works

- The dashboard loads the incident from a server database. Explicit **Save incident** saves inputs, synthetic observations and demo review state. Unsaved edits are identified separately.
- Changed inputs append an immutable R001/R002/... snapshot with a UTC timestamp and assumed-demo evidence. Saving observations/reviews alone preserves the input revision.
- **Run demo assessment** runs only against saved inputs. Jobs retain their exact revision, adapter version, timestamps, terminal reason and explicit `calculated: false` / `illustrative` evidence.
- Exact propylene tanker presets A/B return their hand-authored illustration. Missing/out-of-range numeric inputs, LPG, CNG, storage and other edits return `unsupported` with a reason and no geometry.
- Saving new inputs makes the previous assessment stale. Unsaved input edits, stale/failed/unsupported/not-run results and request errors suppress the map area. JSON and HTML exports carry the backend history and never reuse an unavailable assessment image.
- The activity view shows saved input revisions, jobs and timestamped queued/running/terminal events. Historical jobs remain associated with their original inputs. Reopening history loads a draft rather than changing the old snapshot.

## API and storage

`/api/incident` supports:

| Method | Behaviour |
|---|---|
| GET | Initialize/load D-001; return the saved incident and derived assessment status. |
| PUT | Save `{ expectedVersion, workspace }`; append a revision when inputs changed. |
| POST | Assess saved inputs using `{ expectedVersion }`; return the labelled result or blocking reason. |

All responses disable caching. Server validation bounds inputs, rejects forged non-synthetic observations and reconstructs the allowed workspace fields. Browser-supplied results, jobs, versions and history are not trusted as persisted assessment records.

Local D1 provides SQLite persistence under `website/.wrangler/state`. A schema migration creates one `incidents` table with ID, version and a bounded JSON aggregate containing workspace, immutable input revisions, jobs and events. Keeping the single incident in one aggregate makes each compare-and-swap write atomic; it is a deliberate first-milestone design, not a normalized multi-agency schema. The service appends revisions/history; clients cannot replace them. Database-level append-only enforcement is not claimed.

Each mutation requires the saved version. A concurrent update returns HTTP 409 rather than overwriting another request. The UI retains the draft and offers an explicitly labelled reload/discard action. A failed request never silently switches back to browser-only persistence.

The illustrative adapter completes synchronously in the HTTP request. Queued, running and terminal transitions are separately persisted; there is no background worker or artificial progress timer. A queued/running job left by an interruption is recovered to failed on the next request after 60 seconds, and can then be retried. Inputs cannot be changed while that job is active. The history is bounded at 200 input revisions, 400 jobs and a bounded event budget; reaching a bound returns an explanation and asks for export.

The API accepts localhost/loopback hosts only and rejects cross-origin browser requests. It does not provide authentication, user separation, agency roles, production authorization, automated backup or live synchronization between tabs. A loopback process able to call the API can access the local demo; host checks are not a replacement for authentication. The UI refreshes on explicit reload/save/assessment, rather than polling other clients.

## Local setup and evidence

Use the [website run instructions](../website/README.md). The generated schema/Drizzle metadata are versioned; local database files are ignored. The local migration command uses `--local` and the same database ID/state directory as the preview. No hosted database migration or website deployment was performed.

Validation includes 13 passing domain/API/storage tests, TypeScript and production build. The storage tests execute the generated SQL using real SQLite, reopen a file-backed database, exercise competing updates, recover an interrupted job, and check unsupported/no-result and export protections. Browser verification covers not-run -> completed A -> edited input hidden -> saved/stale -> unsupported CNG -> saved/completed B, synthetic-observation saving and saved revision/job/event history. A real local server restart preserved all three saved input revisions, three jobs and the synthetic observation. The downloaded JSON record was checked for this history, illustrative evidence, `calculated: false`, and null physical thresholds/distances. The local migration command also correctly reported no pending migrations on a second run. The history pane was capped after browser inspection showed it stretching the map.

The existing physics research is unchanged and disconnected. This milestone proves the incident-to-demo-result software chain; it does not qualify dispersion, radiation, blast or valley predictions.

## API boundary hardening — 14 November 2026

Mutation bodies are streamed with a 256,000-byte UTF-8 limit before JSON parsing. Exact application/json media types (with optional parameters), JSON objects and positive safe-integer versions are required before database initialization or interrupted-job recovery. Invalid requests cannot trigger those writes. Invalid saved numeric drafts remain allowed but assessments return unsupported without geometry. Regression coverage now totals 15 passing tests; TypeScript also passes.

## Assessment retries

POST remains compatible with `{ expectedVersion }`: for this single-incident endpoint, one accepted assessment intent is identified by its starting incident version. Each new job persists `requestedVersion` atomically with queue creation. Repeating that version returns the original job ID in `requestJobId` and the latest incident/assessment view without executing the adapter again. A concurrent queue-write loser reads the winning job. Replays can observe queued/running status; callers can GET for completion. The current assessment view always describes current saved state, so a historical retry cannot restore stale geometry.

A deliberate new assessment uses the latest incident version. Failed and unsupported jobs replay their saved status; retrying the calculation requires a new version-based intent. Old stored jobs without requestedVersion remain readable but cannot be retroactively deduplicated: stale requests still receive 409. No schema migration or in-memory retry cache is needed. Keys remain bounded by the existing 400-job history cap. This contract applies only to the current POST whose inputs come entirely from the saved revision; future configurable assessment payloads must extend the intent identity.

CLI regression tests cover lost responses, concurrent duplicates, newer revisions, terminal failures/unsupported results and legacy jobs. Browser verification remains excluded by the user's no-computer-control instruction.

## Interrupted jobs and storage failures

The 60-second recovery lease uses the same injected clock as job timestamps and expires at the boundary. Recovery uses bounded compare-and-swap attempts; a competing recovery or terminal completion is re-read and preserved, so concurrent readers append only one failure event. Recovery remains request-driven, with no background worker.

After a running/terminal write error, the API reads persisted state before marking the job failed. A completed write with a lost acknowledgement keeps its committed completion. A still-active job receives a failure only if that transition can be persisted. Continued storage/read failure returns 503 without an incident/result payload; the active job remains recoverable after the database returns and its lease expires. An ambiguous queue write returns 503; retrying the same starting version finds any committed job instead of creating another. No in-memory result substitutes for saved evidence.

Fault-injection tests exercise before/after-commit failures at queue, running and completion writes, persistent recovery outages, failed cleanup, concurrent recoveries, lease boundaries and a completion winning against recovery. These use disposable SQLite databases, not the user's local incident database.

## Export provenance and stale-result consistency

The dashboard now uses one tested incident export builder for JSON and standalone HTML. Export schema version 2 adds export time, incident version, immutable saved input revision and timestamp, assessment job/revision, initiating version, adapter version, job timestamps, units, coordinate ordering and explicit assumed/illustrative evidence. The source workspace schema remains version 1. Export snapshots are detached copies and cannot mutate saved history or shared fixture data.

Exports describe the last backend snapshot loaded by this browser; exporting does not fetch or certify the latest state in another tab. Missing backend state and request errors are unavailable. Changed input drafts are unsaved-inputs. Not-run, queued, running, failed, unsupported and stale states keep their actual status/reason and include no usable geometry or fixture ID. Unsaved observations/reviews are labelled as drafts; matching saved inputs can still refer to their completed illustrative job. Saved history is separately identified.

Map captures carry job/revision identity and are included only for the matching completed assessment. HTML uses the same status/reason as JSON instead of calling every unavailable state outdated. Captures from earlier jobs/revisions are excluded. Regression tests cover all unavailable states, provenance, snapshot isolation, unsaved notes and escaped HTML. CLI tests/typecheck/build passed; no browser or computer-control verification was performed under the user's instruction.
