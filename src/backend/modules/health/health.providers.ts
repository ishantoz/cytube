import type { AppEnv } from "../../env";

export type HealthProviders = {
	db: D1Database;
	storage: R2Bucket;
	kv: KVNamespace;
};

export function createHealthProviders(
	env: AppEnv["Bindings"],
): HealthProviders {
	return {
		db: env.DB,
		storage: env.ASSETS,
		kv: env.KV,
	};
}
