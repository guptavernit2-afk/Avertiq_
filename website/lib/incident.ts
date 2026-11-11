import { FIXTURES, PRESETS, DEMO_LOCATION, TRAINING_LABEL, initialWorkspace, inputsMatch, loadPreset, restoreWorkspace, type Inputs, type PresetId, type Workspace } from './demo.ts';

export type SavedRevision = { id: string; inputs: Inputs; createdAt: string; evidence: 'assumed-demo' };
export type Job = {
  id: string; revisionId: string; status: 'queued' | 'running' | 'completed' | 'unsupported' | 'failed';
  createdAt: string; updatedAt: string; reason: string; fixture: PresetId | null;
  adapter: 'illustrative-fixture-v1'; calculated: false; evidence: 'illustrative';
};
export type IncidentEvent = { id: number; at: string; type: string; revisionId: string; jobId?: string; message: string };
export type Incident = {
  schemaVersion: 1; id: 'D-001'; version: number; label: typeof TRAINING_LABEL;
  location: typeof DEMO_LOCATION; workspace: Workspace; currentRevisionId: string;
  revisions: SavedRevision[]; jobs: Job[]; events: IncidentEvent[];
};
export class IncidentError extends Error {
  status: number;
  constructor(message: string, status = 400) { super(message); this.status = status; }
}
export const clone = <T,>(value: T): T => structuredClone(value);
export function event(state: Incident, at: string, type: string, message: string, jobId?: string) {
  state.events.push({ id: state.events.length + 1, at, type, message, revisionId: state.currentRevisionId, ...(jobId ? { jobId } : {}) });
}
export function createIncident(at: string): Incident {
  const workspace = initialWorkspace();
  const state: Incident = { schemaVersion: 1, id: 'D-001', version: 1, label: TRAINING_LABEL, location: clone(DEMO_LOCATION), workspace, currentRevisionId: 'R001', revisions: [{ id: 'R001', inputs: clone(workspace.inputs), createdAt: at, evidence: 'assumed-demo' }], jobs: [], events: [] };
  event(state, at, 'created', 'Training incident created. Preset A is assumed; no assessment has run.');
  return state;
}
export function parseWorkspace(value: unknown): Workspace {
  const parsed = restoreWorkspace(JSON.stringify(value));
  if (!parsed) throw new IncidentError('Invalid workspace. Use bounded input strings and labelled synthetic observations.');
  const i = parsed.inputs;
  if (!['Propylene', 'LPG', 'CNG'].includes(i.chemical) || !['Stationary road tanker', 'Fixed storage vessel', 'Cylinder / cascade'].includes(i.asset) || !['North','Northeast','East','Southeast','South','Southwest','West','Northwest'].includes(i.windFrom)) throw new IncidentError('Unknown chemical, asset or wind direction.');
  // Match the saved source values, not a browser-supplied preset selector.
  // Manually entering B's weather while A is selected must still render B.
  for (const id of ['A','B'] as const) if (inputsMatch(parsed.inputs, PRESETS[id])) return loadPreset(parsed, id);
  return parsed;
}
export function busy(state: Incident) { return state.jobs.some(j => j.status === 'queued' || j.status === 'running'); }
export function saveWorkspace(original: Incident, value: unknown, at: string): Incident {
  if (busy(original)) throw new IncidentError('Assessment in progress. Reload before saving.', 409);
  if (original.revisions.length >= 200 || original.events.length >= 1800) throw new IncidentError('This bounded demo history is full. Export the incident before continuing.', 409);
  const state = clone(original);
  const workspace = parseWorkspace(value);
  const previous = state.revisions.find(r => r.id === state.currentRevisionId)!;
  if (!inputsMatch(previous.inputs, workspace.inputs)) {
    state.currentRevisionId = `R${String(state.revisions.length + 1).padStart(3, '0')}`;
    state.revisions.push({ id: state.currentRevisionId, inputs: clone(workspace.inputs), createdAt: at, evidence: 'assumed-demo' });
    event(state, at, 'inputs-saved', 'New assumed input revision saved. Earlier assessments are retained as historical.');
  } else {
    event(state, at, 'workspace-saved', 'Demo observations and review state saved; input revision unchanged.');
  }
  state.workspace = workspace;
  return state;
}
export function demoEligibility(inputs: Inputs): { fixture: PresetId | null; reason: string } {
  const fields: [keyof Inputs, number, number][] = [['releaseRate',0,100000],['duration',0,100000],['windSpeed',0,1000],['temperature',-273.15,1000]];
  for (const [key, minimum, maximum] of fields) {
    const raw = inputs[key].trim(); const number = Number(raw);
    if (!raw || !Number.isFinite(number)) return { fixture: null, reason: `${key} is missing or not a finite number. Save corrected inputs; no result is available.` };
    if (number < minimum || number > maximum || (key === 'temperature' && number === minimum) || ((key === 'releaseRate' || key === 'duration') && number === 0)) return { fixture: null, reason: `${key} is outside this demo's permitted range. No result is available.` };
  }
  for (const fixture of ['A','B'] as const) if (inputsMatch(inputs, PRESETS[fixture])) return { fixture, reason: `Prepared illustration ${fixture} only. No physics was calculated; missing tank inventory, pressure, phase and opening remain unresolved.` };
  return { fixture: null, reason: 'These inputs do not match documented propylene tanker preset A or B. LPG, CNG, storage and other edited scenarios have no connected physics or demo result.' };
}
export function queueAssessment(original: Incident, id: string, at: string): Incident {
  if (busy(original)) throw new IncidentError('Assessment already in progress. Reload its status.', 409);
  if (original.jobs.length >= 400 || original.events.length >= 1800) throw new IncidentError('Demo assessment history is full. Export before continuing.', 409);
  const state = clone(original);
  state.jobs.push({ id, revisionId: state.currentRevisionId, status: 'queued', createdAt: at, updatedAt: at, reason: 'Queued for the illustrative adapter; no physics engine connected.', fixture: null, adapter: 'illustrative-fixture-v1', calculated: false, evidence: 'illustrative' });
  event(state, at, 'assessment-queued', 'Illustrative assessment queued.', id);
  return state;
}
export function transitionJob(original: Incident, id: string, status: 'running' | 'completed' | 'unsupported' | 'failed', at: string, failureReason?: string): Incident {
  const state = clone(original); const job = state.jobs.find(j => j.id === id);
  if (!job || !((job.status === 'queued' && (status === 'running' || status === 'failed')) || (job.status === 'running' && status !== 'running'))) throw new IncidentError('Invalid assessment transition.', 409);
  const revision = state.revisions.find(r => r.id === job.revisionId)!;
  const eligible = demoEligibility(revision.inputs);
  if (status === 'completed' && !eligible.fixture) throw new IncidentError('Unsupported inputs cannot produce a completed result.', 409);
  job.status = status; job.updatedAt = at;
  job.fixture = status === 'completed' ? eligible.fixture : null;
  job.reason = status === 'running' ? 'Checking saved inputs against the two illustrative presets.' : status === 'failed' ? (failureReason ?? 'Assessment failed. No result is available.') : eligible.reason;
  event(state, at, `assessment-${status}`, job.reason, id);
  return state;
}
export function assessmentView(state: Incident) {
  const job = state.jobs.at(-1);
  const status = !job ? 'not-run' : job.revisionId !== state.currentRevisionId ? 'stale' : job.status;
  return { status, job: job ?? null, calculated: false as const, evidence: 'illustrative' as const,
    geometry: status === 'completed' && job?.fixture ? { type: 'Polygon' as const, coordinates: [clone(FIXTURES[job.fixture])] } : null,
    threshold: null, hazardDistance: null, terrainAffectsPhysics: false,
    reason: status === 'not-run' ? 'Saved inputs await a demo assessment.' : status === 'stale' ? 'Saved inputs changed. Previous assessment is historical; run a new demo assessment.' : job!.reason,
  };
}
