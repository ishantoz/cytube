import { copyFileSync, existsSync, mkdirSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

function findSqliteFiles(dir) {
	if (!existsSync(dir)) return [];
	const out = [];
	for (const name of readdirSync(dir, { withFileTypes: true })) {
		const path = join(dir, name.name);
		if (name.isDirectory()) {
			out.push(...findSqliteFiles(path));
			continue;
		}
		if (name.name.endsWith(".sqlite") && name.name !== "metadata.sqlite") {
			out.push({ path, mtime: statSync(path).mtimeMs });
		}
	}
	return out;
}

const studioDb = resolve("prisma/local.db");
const databases = findSqliteFiles(resolve(".wrangler/state/v3/d1")).sort(
	(a, b) => b.mtime - a.mtime,
);

if (databases.length === 0) {
	console.error("No local D1 database found.");
	console.error("Run: pnpm db:migrate");
	process.exit(1);
}

mkdirSync(resolve("prisma"), { recursive: true });
copyFileSync(databases[0].path, studioDb);

const url = pathToFileURL(studioDb).href;
console.log("Prisma Studio → local D1 snapshot");
console.log(`Source: ${databases[0].path}`);
console.log(`Studio: ${studioDb}\n`);

const result = spawnSync("pnpm", ["exec", "prisma", "studio", "--url", url], {
	stdio: "inherit",
	env: process.env,
});

process.exit(result.status ?? 1);
