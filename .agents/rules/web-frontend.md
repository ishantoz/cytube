# Web Frontend Rules

UI is Jinja templates under `app/web/templates/` plus `app/web/static/app.js`.
HTML routes live in `app/web/routes.py`. Inspect and downloads are JSON under `/api`.

## Structure

- `app/web/templates/base.html` — header, nav, footer, download stack
- `app/web/templates/platform.html` — URL form (`#inspect-form`, `data-platform`)
- `app/web/templates/partials/error.html` — unknown-platform HTML 404
- `app/web/static/app.js` — inspect fetch + table render; concurrent jobs, SSE, confirm-to-cancel
- `app/web/routes.py` — `GET /`, `GET /{platform}`

## Styling

- Tailwind CDN (`@tailwindcss/browser@4`) + Flowbite 4 CSS/JS
- Light published-site look (text header/footer, few icons)

## Pages

| Route | Purpose |
| --- | --- |
| `/youtube` (and other platform keys) | inspect + download |
| `/` | redirect to YouTube |

## Inspect and downloads

- Form `fetch`es `POST /api/{platform}/inspect` and renders title/formats in `#results`
- Empty or invalid inspect shows `{error}` text in `#results` (not an HTML fragment swap)
- Download buttons `POST /api/{platform}/jobs` then SSE `/api/jobs/{id}/events`
- Bottom-right stack of concurrent job cards (not a centered overlay)
- Cancel shows `confirm()` then `POST /api/jobs/{id}/cancel`
- No HTMX

## Do not

- Call yt-dlp from `web/`
- Port Cloudflare Astro/Next room UI into this portal without a spec
- Import Python extractors from the browser
- Restore HTMX inspect
