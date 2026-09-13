/** Runtime contract for the `health_checks` D1 table (Prisma: HealthCheck). */

export const HEALTH_TABLE = "health_checks";
export const HEALTH_KIND = "health";
export const HEALTH_STORAGE_KEY = "health/ping.txt";
export const HEALTH_KV_KEY = "health:ping";

export type HealthCheckRow = {
	kind: string;
	checked_at: string;
};

export const upsertHealthCheckSql = `
	INSERT INTO ${HEALTH_TABLE} (kind, checked_at) VALUES (?, ?)
	ON CONFLICT(kind) DO UPDATE SET checked_at = excluded.checked_at
`;

export const selectHealthCheckSql = `
	SELECT checked_at FROM ${HEALTH_TABLE} WHERE kind = ?
`;
