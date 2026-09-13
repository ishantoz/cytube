-- Probe table for GET /api/health (D1 write/read).
CREATE TABLE "health_checks" (
    "kind" TEXT NOT NULL PRIMARY KEY,
    "checked_at" TEXT NOT NULL
);
