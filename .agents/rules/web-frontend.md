# Web Frontend Rules

UI is Astro at `src/pages/`.

## Structure

- `src/pages/index.astro` — HTML stub
- New UI pages go in `src/pages/`. Do not rebuild the old Next channel
  list or `/r/[name]` room unless a spec says so.

## Styling

- Tokens: `prototypes/theme.css`. 6b ports them into the app stylesheet.
- Dark media-room: player primary, playlist and chat secondary.

## Pages

| Route | Purpose |
| --- | --- |
| `/` | Astro stub until 6b (see `prototypes/home.html`) |
| `/api/*` | Hono (not Astro pages) |

## Do not

- Port the deleted Next components (`Header`, `ChannelCard`, `VideoPlayer`,
  `Playlist`, `Chat`) without a spec
- Import Prisma into page files
