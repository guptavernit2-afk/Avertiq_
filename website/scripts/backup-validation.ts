import { z } from 'zod';
import { DEMO_LOCATION, TRAINING_LABEL, inputsMatch } from '../lib/demo.ts';
import { demoEligibility, parseWorkspace, type Incident } from '../lib/incident.ts';

const time = z.string().datetime();
const id = z.string().min(1).max(200);
const inputs = z.object({ chemical: z.enum(['Propylene','LPG','CNG']), asset: z.enum(['Stationary road tanker','Fixed storage vessel','Cylinder / cascade']), releaseRate: z.string().max(80), duration: z.string().max(80), windSpeed: z.string().max(80), windFrom: z.enum(['North','Northeast','East','Southeast','South','Southwest','West','Northwest']), temperature: z.string().max(80) }).strict();
const revision = z.object({id, inputs, createdAt:time, evidence:z.literal('assumed-demo')}).strict();
const job = z.object({id, revisionId:id, requestedVersion:z.number().int().positive().safe().optional(), status:z.enum(['queued','running','completed','unsupported','failed']), createdAt:time, updatedAt:time, reason:z.string().max(4000), fixture:z.enum(['A','B']).nullable(), adapter:z.literal('illustrative-fixture-v1'), calculated:z.literal(false), evidence:z.literal('illustrative')}).strict();
const event = z.object({id:z.number().int().positive(), at:time, type:z.enum(['created','inputs-saved','workspace-saved','assessment-queued','assessment-running','assessment-completed','assessment-unsupported','assessment-failed']), revisionId:id, jobId:id.optional(), message:z.string().max(4000)}).strict();
const schema = z.object({schemaVersion:z.literal(1), id:z.literal('D-001'), version:z.number().int().positive().safe(), label:z.literal(TRAINING_LABEL), location:z.object({lng:z.number(),lat:z.number(),label:z.string(),source:z.string()}).strict(), workspace:z.unknown(), currentRevisionId:id, revisions:z.array(revision).min(1).max(200), jobs:z.array(job).max(400), events:z.array(event).min(1).max(1803)}).strict();
function requireCondition(value: unknown, message: string): asserts value { if (!value) throw new Error(`Invalid incident backup: ${message}`); }
export function validateIncident(value: unknown): Incident {
  const parsed=schema.parse(value);
  const workspace=parseWorkspace(parsed.workspace);
  requireCondition(JSON.stringify(workspace)===JSON.stringify(parsed.workspace),'workspace is not the canonical saved format');
  requireCondition(JSON.stringify(parsed.location)===JSON.stringify(DEMO_LOCATION),'unexpected demo location');
  const revisions=new Map(parsed.revisions.map(r=>[r.id,r]));
  requireCondition(revisions.size===parsed.revisions.length,'duplicate revisions');
  parsed.revisions.forEach((r,i)=>requireCondition(r.id===`R${String(i+1).padStart(3,'0')}`,'revision order'));
  requireCondition(parsed.currentRevisionId===parsed.revisions.at(-1)!.id,'current revision must be latest');
  requireCondition(inputsMatch(workspace.inputs,revisions.get(parsed.currentRevisionId)!.inputs),'workspace differs from saved inputs');
  const jobs=new Map(parsed.jobs.map(j=>[j.id,j]));
  requireCondition(jobs.size===parsed.jobs.length,'duplicate jobs');
  const requests=parsed.jobs.flatMap(j=>j.requestedVersion===undefined?[]:[j.requestedVersion]);
  requireCondition(new Set(requests).size===requests.length && requests.every(v=>v<parsed.version),'invalid request versions');
  requireCondition(parsed.jobs.filter(j=>j.status==='queued'||j.status==='running').length<=1,'multiple active jobs');
  for (const j of parsed.jobs) {
    const r=revisions.get(j.revisionId);
    requireCondition(r,'job has missing revision');
    requireCondition(Date.parse(j.updatedAt)>=Date.parse(j.createdAt),'job timestamps reversed');
    requireCondition(j.status==='completed' ? j.fixture!==null && demoEligibility(r.inputs).fixture===j.fixture : j.fixture===null,'job result contradicts inputs/status');
    if (j.status==='queued'||j.status==='running') requireCondition(j===parsed.jobs.at(-1) && j.revisionId===parsed.currentRevisionId,'active job is not current');
  }
  parsed.events.forEach((e,i)=>{
    requireCondition(e.id===i+1 && revisions.has(e.revisionId),'event sequence or revision');
    if(e.type.startsWith('assessment-')) requireCondition(e.jobId && jobs.get(e.jobId)?.revisionId===e.revisionId,'event has missing/mismatched job');
    else requireCondition(e.jobId===undefined,'workspace event names a job');
  });
  requireCondition(parsed.events[0].type==='created','creation event missing');
  for (const j of parsed.jobs) {
    const types=parsed.events.filter(e=>e.jobId===j.id).map(e=>e.type);
    const expected=j.status==='queued'?['assessment-queued']:j.status==='running'?['assessment-queued','assessment-running']:j.status==='failed'&&types.length===2?['assessment-queued','assessment-failed']:['assessment-queued','assessment-running',`assessment-${j.status}`];
    requireCondition(JSON.stringify(types)===JSON.stringify(expected),'job event transitions disagree with status');
  }
  return value as Incident;
}
