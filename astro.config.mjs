import cloudflare from "@astrojs/cloudflare";
import { defineConfig } from "astro/config";

export default defineConfig({
	adapter: cloudflare({
		imageService: "passthrough",
	}),
	session: false,
	vite: {
		optimizeDeps: {
			include: [
				"astro/app",
				"astro/app/manifest",
				"astro/assets",
				"astro/assets/services/noop",
				"@astrojs/cloudflare/entrypoints/server",
			],
		},
	},
	server: {
		port: 8787,
		cors: false,
	},
});
