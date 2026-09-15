import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';
import dotenv from 'dotenv';

dotenv.config();

// Connections are lazy. This local default lets database-independent routes
// start before first-run database setup is complete.
const databaseUrl =
  process.env.POSTGRES_URL ??
  'postgres://engco:engco@127.0.0.1:5432/engco';

export const client = postgres(databaseUrl);
export const db = drizzle(client, { schema });
