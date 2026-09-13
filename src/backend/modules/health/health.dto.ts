export type CheckStatus = "ok" | "error";

export type HealthReportDto = {
	status: "ok" | "error";
	database: CheckStatus;
	storage: CheckStatus;
	kv: CheckStatus;
};
