#!/usr/bin/env bash
# Cursor MCP host often lacks fnm/pnpm on PATH. Keep this launcher next to mcp.json.
set -euo pipefail
export PATH="${HOME}/Library/pnpm:${HOME}/.local/share/fnm/aliases/default/bin:/opt/homebrew/bin:/usr/local/bin:${PATH}"
exec npx -y @playwright/mcp@latest \
  --browser=chrome \
  --viewport-size=1440x900 \
  --console-level=warning \
  "$@"
