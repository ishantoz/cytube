import { Hono } from "hono";
import { logger } from "hono/logger";
import { env } from "cloudflare:workers";
import type { AppEnv } from "./env";
import { registerHealthModule } from "./modules/health";

export type { AppEnv } from "./env";

export const app = new Hono<AppEnv>().basePath("/api");

app.use("*", logger());
registerHealthModule(app);
app.notFound((c) => c.json({ error: "Not found" }, 404));

export function handleApi(
	request: Request,
	executionCtx: ExecutionContext,
): Promise<Response> | Response {
	return app.fetch(request, env, executionCtx);
}
