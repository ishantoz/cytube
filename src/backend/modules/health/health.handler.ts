import type { Context } from "hono";
import type { AppEnv } from "../../env";
import { createHealthProviders } from "./health.providers";
import { getHealthReport } from "./health.service";

export async function getHealthHandler(c: Context<AppEnv>) {
	const report = await getHealthReport(createHealthProviders(c.env));
	return c.json(report, report.status === "ok" ? 200 : 503);
}
