export type AppEnv = {
	Bindings: {
		DB: D1Database;
		ASSETS: R2Bucket;
		SESSION: KVNamespace;
		KV: KVNamespace;
	};
};
