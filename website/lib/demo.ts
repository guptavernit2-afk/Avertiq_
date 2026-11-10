export const TRAINING_LABEL = 'Training demo — simulated incident and assessment';
export const DEMO_LOCATION = { lng: 73.3465372, lat: 18.76449685, label: 'Adoshi corridor · approximate demo pin', source: 'OpenStreetMap way 42680772, version 12; collected 8 November 2026. Mapped tunnel midpoint, not verified accident coordinates.' };
export type Inputs = { chemical: string; asset: string; releaseRate: string; duration: string; windSpeed: string; windFrom: string; temperature: string };
export type PresetId = 'A' | 'B';
export type Observation = { id: string; text: string; kind: 'Field report' | 'Weather report'; time: string; synthetic: true };
export type Revision = { id: PresetId; inputs: Inputs; time: string; fixtureId: string; evidence: 'illustrative' };
export type Workspace = { version: 1; inputs: Inputs; revisions: Revision[]; activeRevision: PresetId; observations: Observation[]; reviewedPlaces: string[] };
export const PRESETS: Record<PresetId, Inputs> = {
  A: { chemical: 'Propylene', asset: 'Stationary road tanker', releaseRate: '0.1', duration: '10', windSpeed: '2', windFrom: 'West', temperature: '25' },
  B: { chemical: 'Propylene', asset: 'Stationary road tanker', releaseRate: '0.1', duration: '10', windSpeed: '2', windFrom: 'Southwest', temperature: '25' },
};
export const PLACES = [
  { id: 'school', name: 'Demo school', type: 'Education', coordinates: [73.3522, 18.7655] as [number, number], note: 'Fictional review site. Occupancy, contacts and accessibility are unconfirmed.' },
  { id: 'homes', name: 'Demo housing', type: 'Residential', coordinates: [73.3500, 18.7606] as [number, number], note: 'Fictional residential cluster. No verified population or occupancy data.' },
  { id: 'clinic', name: 'Demo clinic', type: 'Healthcare', coordinates: [73.3405, 18.7677] as [number, number], note: 'Fictional clinic. Capacity, availability and access are unconfirmed.' },
];
// Hand-authored illustrations. These vertices encode no physical threshold or hazard distance.
export const FIXTURES = {
  A: [[73.3465372,18.76449685],[73.3490,18.7660],[73.3544,18.7663],[73.3574,18.7646],[73.3542,18.7629],[73.3490,18.7630],[73.3465372,18.76449685]],
  B: [[73.3465372,18.76449685],[73.3474,18.7674],[73.3517,18.7691],[73.3555,18.7675],[73.3542,18.7646],[73.3501,18.7638],[73.3465372,18.76449685]],
};
export function inputsMatch(a: Inputs, b: Inputs) { return (Object.keys(PRESETS.A) as (keyof Inputs)[]).every(key => a[key] === b[key]); }
export function fixtureIsCurrent(workspace: Workspace) { return inputsMatch(workspace.inputs, PRESETS[workspace.activeRevision]); }
export function initialWorkspace(): Workspace {
  return { version: 1, inputs: { ...PRESETS.A }, revisions: [{ id: 'A', inputs: { ...PRESETS.A }, time: 'T+00', fixtureId: 'D-001-illustration-A', evidence: 'illustrative' }], activeRevision: 'A', observations: [], reviewedPlaces: [] };
}
export function loadPreset(workspace: Workspace, id: PresetId): Workspace {
  const snapshot: Revision = { id, inputs: { ...PRESETS[id] }, time: id === 'A' ? 'T+00' : 'T+05', fixtureId: `D-001-illustration-${id}`, evidence: 'illustrative' };
  return { ...workspace, activeRevision: id, inputs: { ...PRESETS[id] }, revisions: workspace.revisions.some(r => r.id === id) ? workspace.revisions : [...workspace.revisions, snapshot] };
}
export function restoreWorkspace(raw: string | null): Workspace | null {
  if (!raw || raw.length > 100000) return null;
  try {
    const value = JSON.parse(raw) as Workspace;
    if (value?.version !== 1 || !['A','B'].includes(value.activeRevision) || !value.inputs || !Array.isArray(value.revisions) || !Array.isArray(value.observations) || !Array.isArray(value.reviewedPlaces)) return null;
    if (!(Object.keys(PRESETS.A) as (keyof Inputs)[]).every(k => typeof value.inputs[k] === 'string' && value.inputs[k].length <= 80)) return null;
    if (value.revisions.length > 2 || !value.revisions.some(r => r.id === value.activeRevision) || value.revisions.some(r => !r || !['A','B'].includes(r.id) || !r.inputs || !inputsMatch(r.inputs, PRESETS[r.id]) || r.evidence !== 'illustrative' || r.fixtureId !== `D-001-illustration-${r.id}`)) return null;
    if (new Set(value.revisions.map(r => r.id)).size !== value.revisions.length) return null;
    if (value.observations.length > 100 || value.observations.some(o => !o || typeof o.id !== 'string' || typeof o.text !== 'string' || !o.text.trim() || o.text.length > 1500 || o.synthetic !== true || !['Field report','Weather report'].includes(o.kind) || !/^T\+\d{2,3}$/.test(o.time))) return null;
    if (value.reviewedPlaces.some(id => !PLACES.some(p => p.id === id))) return null;
    return { version: 1, inputs: Object.fromEntries((Object.keys(PRESETS.A) as (keyof Inputs)[]).map(key => [key, value.inputs[key]])) as Inputs, activeRevision: value.activeRevision, revisions: value.revisions.map(r => ({ id: r.id, inputs: { ...PRESETS[r.id] }, time: r.id === 'A' ? 'T+00' : 'T+05', fixtureId: `D-001-illustration-${r.id}`, evidence: 'illustrative' })), observations: value.observations.map(o => ({ id: o.id, text: o.text, kind: o.kind, time: o.time, synthetic: true })), reviewedPlaces: [...new Set(value.reviewedPlaces)] };
  } catch { return null; }
}
export function exportRecord(workspace: Workspace) {
  const current = fixtureIsCurrent(workspace);
  return { label: TRAINING_LABEL, schemaVersion: 1, incident: 'D-001', synthetic: true, location: DEMO_LOCATION, evidenceStatus: 'illustrative', assessment: { status: current ? 'illustrative' : 'stale', fixtureId: current ? `D-001-illustration-${workspace.activeRevision}` : null, threshold: null, hazardDistance: null, calculated: false, terrainAffectsPhysics: false, geometry: current ? { type: 'Polygon', coordinates: [FIXTURES[workspace.activeRevision]] } : null }, inputEvidence: { chemical: 'Assumed for demo', releaseRate: 'Assumed kg/s', duration: 'Assumed minutes', weather: 'Simulated', inventory: 'Unavailable', tankPressure: 'Unavailable', opening: 'Unavailable', releasePhase: 'Unavailable' }, ...workspace, limitations: ['No physics engine connected.', 'Prepared areas are illustrations, not evacuation boundaries.', 'Fictional places do not establish real occupancy or access.', 'Terrain provides geographic context only.', 'No live tracking, government connection or public notification.'] };
}
export function escapeHtml(text: string) { return text.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!)); }
export function handoverHtml(workspace: Workspace, mapImage?: string): string {
  const record = exportRecord(workspace);
  const row = (label: string, value: string) => `<tr><th>${escapeHtml(label)}</th><td>${escapeHtml(value)}</td></tr>`;
  const image = record.assessment.status === 'illustrative' && mapImage && /^data:image\/png;base64,[a-zA-Z0-9+/=]+$/.test(mapImage) ? `<figure><img alt="Geographic context with a labelled illustrative assessment, not a calculated hazard" src="${mapImage}"><figcaption>Training demo — illustrative area ${workspace.activeRevision}. Geographic context: © OpenStreetMap contributors; terrain: <a href="https://mapterhorn.com/attribution">Mapterhorn / source attribution</a>. Pin is approximate; places are fictional. No calculated hazard distance.</figcaption></figure>` : '<p>Map image unavailable or assessment outdated. Refer to the attributed map in the dashboard.</p>';
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Avertiq D-001 · Demo handover</title><style>body{font:15px/1.6 system-ui;color:#18323c;max-width:850px;margin:35px auto;padding:20px}header{border-bottom:2px solid #087970;padding-bottom:14px}.label{padding:10px;background:#fff3d5;font-weight:700}h1{font-size:28px}h2{font-size:19px;margin-top:28px}table{width:100%;border-collapse:collapse}th,td{text-align:left;vertical-align:top;padding:9px;border-bottom:1px solid #d7e1e3}th{width:35%}img{width:100%}figure{margin:20px 0}figcaption{font-size:12px}li{margin-bottom:8px}@media print{.label{position:fixed;top:0;left:0;right:0}body{padding-top:40px}@page{margin:20mm}}</style></head><body><header><div class="label">${TRAINING_LABEL}</div><h1>AVERTIQ / Incident handover</h1><p>D-001 · ${escapeHtml(record.location.label)} · Revision ${workspace.activeRevision}</p></header><h2>Assessment status</h2><p>${record.assessment.status === 'stale' ? 'OUTDATED: inputs differ from the selected preset. No assessment geometry is valid for these inputs.' : 'Prepared illustrative assessment only. No physical model was run.'}</p><h2>Current inputs</h2><table>${row('Cargo / asset', `${workspace.inputs.chemical} / ${workspace.inputs.asset} — assumed for demo`)}${row('Release assumption', `${workspace.inputs.releaseRate} kg/s over ${workspace.inputs.duration} minutes — assumed`)}${row('Weather', `${workspace.inputs.windSpeed} m/s, from ${workspace.inputs.windFrom}; ${workspace.inputs.temperature} °C — simulated`)}${row('Missing information','Inventory, tank pressure, opening size and release phase')}${row('Location evidence',record.location.source)}</table>${image}<h2>Observations — synthetic</h2>${workspace.observations.length ? '<ul>'+workspace.observations.map(o=>`<li>${escapeHtml(o.time)} · ${escapeHtml(o.kind)} · SIMULATED: ${escapeHtml(o.text)}</li>`).join('')+'</ul>' : '<p>No observations recorded.</p>'}<h2>Preserved revisions</h2><table>${workspace.revisions.map(r=>row(`Revision ${r.id} · ${r.time}`,`${r.inputs.chemical}; ${r.inputs.releaseRate} kg/s; wind ${r.inputs.windSpeed} m/s from ${r.inputs.windFrom}; fixture ${r.fixtureId} — illustrative`)).join('')}</table><h2>Place review — fictional sites</h2><ul>${PLACES.map(p=>`<li>${escapeHtml(p.name)}: ${workspace.reviewedPlaces.includes(p.id)?'reviewed in demo':'review pending'}. ${escapeHtml(p.note)}</li>`).join('')}</ul><h2>Limits and pending decisions</h2><ul>${record.limitations.map(l=>`<li>${escapeHtml(l)}</li>`).join('')}<li>Evacuation, shelter instructions and restrictions require authority review; none issued by this demo.</li></ul></body></html>`;
}
