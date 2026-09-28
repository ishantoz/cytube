#!/usr/bin/env bash
# Compare current static-check errors against the recorded adoption baseline.
#
# CyTube: FastAPI download portal. Gate is a Python import/compile smoke
# (no test framework).
#
#   ./.agents/check-baseline.sh          compare against the baseline
#   ./.agents/check-baseline.sh --write  re-record the baseline (needs approval)
set -euo pipefail
cd "$(dirname "$0")/.."
state="blueprint/.state"
mode="${1:-check}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# --- Python compile + import (app) ---
uv run python -m compileall -q app
uv run python -c "from app.main import app"

# Per-file compile errors (empty when green)
: > "$tmp/py.txt"

# --- ESLint (none) ---
echo '[]' > "$tmp/eslint.json"
python3 - "$tmp/eslint.json" "$PWD" > "$tmp/eslint.txt" <<'PY'
import collections, json, sys
report, root = sys.argv[1], sys.argv[2].rstrip("/") + "/"
counts = collections.Counter()
for entry in json.load(open(report)):
    errors = sum(1 for m in entry["messages"] if m["severity"] == 2)
    if errors:
        path = entry["filePath"].replace(root, "")
        counts[path] = errors
for path in sorted(counts):
    print(f"{counts[path]}\t{path}")
PY

if [ "$mode" = "--write" ]; then
  mkdir -p "$state"
  cp "$tmp/py.txt" "$state/py-baseline.txt"
  cp "$tmp/eslint.txt" "$state/eslint-baseline.txt"
  py_total=$(awk -F'\t' '{s+=$2} END {print s+0}' "$state/py-baseline.txt")
  eslint_total=$(awk -F'\t' '{s+=$1} END {print s+0}' "$state/eslint-baseline.txt")
  echo "baseline re-recorded: ${py_total} py, ${eslint_total} eslint"
  exit 0
fi

status=0
for kind in py eslint; do
  base="$state/$kind-baseline.txt"
  now="$tmp/$kind.txt"
  if [ "$kind" = "eslint" ]; then
    before=$(awk -F'\t' '{s+=$1} END {print s+0}' "$base" 2>/dev/null || echo 0)
    after=$(awk -F'\t' '{s+=$1} END {print s+0}' "$now")
  else
    before=$(awk -F'\t' '{s+=$2} END {print s+0}' "$base" 2>/dev/null || echo 0)
    after=$(awk -F'\t' '{s+=$2} END {print s+0}' "$now")
  fi
  printf '%-7s baseline %4d  now %4d\n' "$kind" "$before" "$after"
done

if [ "$status" -ne 0 ]; then
  echo
  echo "NEW errors introduced. Fix them, or record why in the spec."
else
  echo "no new errors against baseline"
fi
exit "$status"
