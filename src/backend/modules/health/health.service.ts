import type { CheckStatus, HealthReportDto } from "./health.dto";
import type { HealthProviders } from "./health.providers";
import {
	HEALTH_KIND,
	HEALTH_KV_KEY,
	HEALTH_STORAGE_KEY,
	selectHealthCheckSql,
	upsertHealthCheckSql,
	type HealthCheckRow,
} from "./health.schema";

async function checkDatabase(db: D1Database): Promise<void> {
	const checkedAt = new Date().toISOString();
	await db
		.prepare(upsertHealthCheckSql)
		.bind(HEALTH_KIND, checkedAt)
		.run();
	const row = await db
		.prepare(selectHealthCheckSql)
		.bind(HEALTH_KIND)
		.first<HealthCheckRow>();
	if (!row?.checked_at) {
		throw new Error("database probe row missing");
	}
}

async function checkStorage(bucket: R2Bucket): Promise<void> {
	const payload = new Date().toISOString();
	await bucket.put(HEALTH_STORAGE_KEY, payload);
	const object = await bucket.get(HEALTH_STORAGE_KEY);
	if (!object || (await object.text()) !== payload) {
		throw new Error("storage probe mismatch");
	}
}

async function checkKv(kv: KVNamespace): Promise<void> {
	const payload = new Date().toISOString();
	await kv.put(HEALTH_KV_KEY, payload);
	const got = await kv.get(HEALTH_KV_KEY);
	if (got !== payload) {
		throw new Error("kv probe mismatch");
	}
}

async function settled(fn: () => Promise<void>): Promise<CheckStatus> {
	try {
		await fn();
		return "ok";
	} catch {
		return "error";
	}
}

export async function getHealthReport(
	providers: HealthProviders,
): Promise<HealthReportDto> {
	const [database, storage, kv] = await Promise.all([
		settled(() => checkDatabase(providers.db)),
		settled(() => checkStorage(providers.storage)),
		settled(() => checkKv(providers.kv)),
	]);
	const status =
		database === "ok" && storage === "ok" && kv === "ok" ? "ok" : "error";
	return { status, database, storage, kv };
}
