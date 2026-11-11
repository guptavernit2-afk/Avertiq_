import { IncidentStore } from './incident-store.ts';
import { IncidentError, assessmentView, busy, demoEligibility, queueAssessment, saveWorkspace, transitionJob, type Incident } from './incident.ts';

const response = (state: Incident) => Response.json({ incident: state, assessment: assessmentView(state) }, { headers: { 'Cache-Control': 'no-store' } });
export function incidentApi(store: IncidentStore, clock = () => new Date().toISOString(), uuid = () => crypto.randomUUID()) {
  return async (request: Request): Promise<Response> => {
    try {
      const url = new URL(request.url);
      if (!['localhost','127.0.0.1','[::1]'].includes(url.hostname)) throw new IncidentError('This single-incident demo API is local-only. Agency authentication is not implemented.', 403);
      if (request.headers.get('sec-fetch-site') === 'cross-site' || (request.headers.has('origin') && request.headers.get('origin') !== url.origin)) throw new IncidentError('Use the same local origin as the dashboard.', 403);
      if (!['GET','PUT','POST'].includes(request.method)) throw new IncidentError('Method not allowed.', 405);
      let state = await store.initialize(clock());
      const active = state.jobs.find(j => j.status === 'queued' || j.status === 'running');
      if (active && Date.now() - Date.parse(active.updatedAt) > 60000) {
        state = await store.write(transitionJob(state, active.id, 'failed', clock(), 'The demo request was interrupted or timed out. No result was retained. Run a new assessment.'), state.version);
      }
      if (request.method === 'GET') return response(state);
      if (!request.headers.get('content-type')?.includes('application/json')) throw new IncidentError('Send application/json.', 415);
      const text = await request.text();
      if (text.length > 256000) throw new IncidentError('Request is too large.', 413);
      let body: { expectedVersion?: number; workspace?: unknown };
      try { body = JSON.parse(text); } catch { throw new IncidentError('Malformed JSON.'); }
      if (!body || !Number.isSafeInteger(body.expectedVersion) || body.expectedVersion! < 1) throw new IncidentError('expectedVersion must identify the saved incident version.');
      if (body.expectedVersion !== state.version) throw new IncidentError('Another tab or request saved this incident. Reload before retrying; your draft remains visible.', 409);
      if (request.method === 'PUT') return response(await store.write(saveWorkspace(state, body.workspace, clock()), state.version));
      if (busy(state)) throw new IncidentError('An assessment is already in progress.', 409);
      const id = uuid();
      state = await store.write(queueAssessment(state, id, clock()), state.version);
      try {
        state = await store.write(transitionJob(state, id, 'running', clock()), state.version);
        const revision = state.revisions.find(r => r.id === state.currentRevisionId)!;
        const status = demoEligibility(revision.inputs).fixture ? 'completed' : 'unsupported';
        state = await store.write(transitionJob(state, id, status, clock()), state.version);
      } catch (error) {
        // A server error never becomes a completed illustration. A crashed process
        // is recovered to failed on the next request after the 60-second lease.
        if (!(error instanceof IncidentError && error.status === 409)) {
          state = await store.write(transitionJob(state, id, 'failed', clock()), state.version);
        } else throw error;
      }
      return response(state);
    } catch (error) {
      const known = error instanceof IncidentError;
      return Response.json({ error: known ? error.message : 'Local incident database unavailable. Check that local migrations have been applied, then reload.' }, { status: known ? error.status : 503, headers: { 'Cache-Control': 'no-store' } });
    }
  };
}
