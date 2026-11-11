import { createIncident, IncidentError, type Incident } from './incident.ts';

export interface Statement {
  bind(...values: (string | number)[]): Statement;
  first<T>(): Promise<T | null>;
  run(): Promise<{ meta: { changes: number } }>;
}
export interface IncidentDatabase { prepare(sql: string): Statement }
export class IncidentStore {
  private db: IncidentDatabase;
  constructor(db: IncidentDatabase) { this.db = db; }
  async read(): Promise<Incident> {
    const row = await this.db.prepare('SELECT payload FROM incidents WHERE id = ?').bind('D-001').first<{ payload: string }>();
    if (!row) throw new IncidentError('Incident has not been initialized.', 404);
    return JSON.parse(row.payload) as Incident;
  }
  async initialize(at: string): Promise<Incident> {
    const state = createIncident(at);
    await this.db.prepare('INSERT OR IGNORE INTO incidents (id, version, payload) VALUES (?, ?, ?)').bind(state.id, state.version, JSON.stringify(state)).run();
    return this.read();
  }
  async write(next: Incident, expectedVersion: number): Promise<Incident> {
    const saved = { ...next, version: expectedVersion + 1 };
    const result = await this.db.prepare('UPDATE incidents SET version = ?, payload = ? WHERE id = ? AND version = ?').bind(saved.version, JSON.stringify(saved), saved.id, expectedVersion).run();
    if (result.meta.changes !== 1) throw new IncidentError('Another request changed this incident. Reload the saved incident before retrying; your draft has not been overwritten.', 409);
    return saved;
  }
}
