import { exportRecord, handoverHtml, escapeHtml, inputsMatch, fixtureIsCurrent, type Workspace } from './demo.ts';
import { assessmentView, clone, type Incident } from './incident.ts';

export type CapturedMap = { dataUrl: string; jobId: string; revisionId: string };
export function incidentExport(workspace: Workspace, state: Incident | null, error = '', exportedAt = new Date().toISOString()) {
  const view = state ? assessmentView(state) : null;
  const revision = state?.revisions.find(r => r.id === state.currentRevisionId);
  const job = view?.job;
  const inputsSaved = !!revision && inputsMatch(workspace.inputs, revision.inputs);
  const status = error ? 'unavailable' : !state ? 'unavailable' : !inputsSaved ? 'unsaved-inputs' : view!.status;
  const allowed = status === 'completed' && job?.fixture === workspace.activeRevision && fixtureIsCurrent(workspace);
  const reason = error || (!state ? 'No saved incident is available.' : !inputsSaved ? 'Unsaved inputs differ from the saved revision. No assessment applies to this draft.' : view!.reason);
  const record = exportRecord(workspace, allowed);
  return clone({ ...record, exportSchemaVersion: 2, exportedAt,
    saved: !!state && JSON.stringify(workspace) === JSON.stringify(state.workspace),
    assessment: { ...record.assessment, status, reason, geometry: allowed ? view!.geometry : null,
      fixtureId: allowed ? record.assessment.fixtureId : null },
    provenance: {
      incidentVersion: state?.version ?? null, savedInputRevisionId: revision?.id ?? null,
      savedInputCreatedAt: revision?.createdAt ?? null, inputsMatchSavedRevision: inputsSaved,
      assessmentJobId: job?.id ?? null, assessmentRevisionId: job?.revisionId ?? null,
      adapterVersion: job?.adapter ?? null, requestedVersion: job?.requestedVersion ?? null,
      jobCreatedAt: job?.createdAt ?? null, jobUpdatedAt: job?.updatedAt ?? null,
      inputEvidence: 'assumed-demo', resultEvidence: 'illustrative', calculated: false,
      units: { releaseRate: 'kg/s', duration: 'minutes', windSpeed: 'm/s', temperature: 'degrees Celsius', windFrom: 'compass direction wind comes from' },
      coordinates: 'WGS84 longitude, latitude', timestamps: 'UTC ISO 8601; T+ observation labels are synthetic relative times',
    },
    backendHistory: state ? { id: state.id, version: state.version, currentRevisionId: state.currentRevisionId, revisions: state.revisions, jobs: state.jobs, events: state.events } : null,
  });
}
export function matchingMap(record: ReturnType<typeof incidentExport>, capture?: CapturedMap) {
  return record.assessment.geometry && capture?.jobId === record.provenance.assessmentJobId && capture?.revisionId === record.provenance.savedInputRevisionId ? capture.dataUrl : undefined;
}
export function incidentHandover(workspace: Workspace, state: Incident | null, error = '', capture?: CapturedMap, exportedAt?: string) {
  const record = incidentExport(workspace, state, error, exportedAt);
  const section = `<h2>Export provenance</h2><p>${record.saved ? 'Saved incident snapshot.' : 'UNSAVED browser draft; saved history below may differ.'}</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${escapeHtml(JSON.stringify({ exportedAt: record.exportedAt, ...record.provenance }, null, 2))}</pre><h2>Saved backend history</h2><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${escapeHtml(JSON.stringify(record.backendHistory, null, 2))}</pre>`;
  return handoverHtml(workspace, matchingMap(record, capture), !!record.assessment.geometry, `${record.assessment.status}: ${record.assessment.reason}`).replace('</body>', section + '</body>');
}
