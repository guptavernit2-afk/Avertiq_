import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core';

// One bounded aggregate keeps a revision, its jobs and history atomic.
// Only the server appends history; version is used for compare-and-swap writes.
export const incidents = sqliteTable('incidents', {
  id: text('id').primaryKey(),
  version: integer('version').notNull(),
  payload: text('payload').notNull(),
});
