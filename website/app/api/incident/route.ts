import { env } from 'cloudflare:workers';
import { incidentApi } from '@/lib/incident-api';
import { IncidentStore } from '@/lib/incident-store';

async function handle(request: Request) {
  if (!env.DB) return Response.json({ error: 'Local incident database binding is unavailable.' }, { status: 503 });
  return incidentApi(new IncidentStore(env.DB))(request);
}
export const GET = handle;
export const PUT = handle;
export const POST = handle;
