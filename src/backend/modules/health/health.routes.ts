import { Hono } from "hono";
import type { AppEnv } from "../../env";
import { getHealthHandler } from "./health.handler";

export const healthRoutes = new Hono<AppEnv>().get("/", getHealthHandler);
