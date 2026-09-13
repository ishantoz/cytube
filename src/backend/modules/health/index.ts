import type { Hono } from "hono";
import type { AppEnv } from "../../env";
import { healthRoutes } from "./health.routes";

export function registerHealthModule(app: Hono<AppEnv>) {
	app.route("/health", healthRoutes);
}

export type { HealthReportDto } from "./health.dto";
