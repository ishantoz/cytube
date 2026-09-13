#!/usr/bin/env bash
# Compare current static-check errors against the recorded adoption baseline.
#
# CyTube: root Astro Worker. Gate is no new tsc errors vs baseline.
#
#   ./.agents/check-baseline.sh          compare against the baseline
#   ./.agents/check-baseline.sh --write  re-record the baseline (needs approval)
set -uo pipefail
cd "$(dirname "$0")/.."
state="blueprint/.state"
mode="${1:-check}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# --- Typecheck (root) ---
pnpm exec tsc --noEmit 2>&1 | grep 'error TS' \
  | sed -E 's/[(:][0-9]+,[0-9]+\).*//' | sort | uniq -c \
  | awk '{printf "%s\t%s\n", $2, $1}' | sort -k1 \
  > "$tmp/tsc.txt"

# --- ESLint (none at root yet) ---
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
  cp "$tmp/tsc.txt" "$state/tsc-baseline.txt"
  cp "$tmp/eslint.txt" "$state/eslint-baseline.txt"
  tsc_total=$(awk -F'\t' '{s+=$2} END {print s+0}' "$state/tsc-baseline.txt")
  eslint_total=$(awk -F'\t' '{s+=$1} END {print s+0}' "$state/eslint-baseline.txt")
  echo "baseline re-recorded: ${tsc_total} tsc, ${eslint_total} eslint"
  exit 0
fi

status=0
for kind in tsc eslint; do
  base="$state/$kind-baseline.txt"
  now="$tmp/$kind.txt"
  before=$(awk -F'\t' '{s+=$2} END {print s+0}' "$base" 2>/dev/null || echo 0)
  if [ "$kind" = "eslint" ]; then
    before=$(awk -F'\t' '{s+=$1} END {print s+0}' "$base" 2>/dev/null || echo 0)
    after=$(awk -F'\t' '{s+=$1} END {print s+0}' "$now")
  else
    after=$(awk -F'\t' '{s+=$2} END {print s+0}' "$now")
  fi
  printf '%-7s baseline %4d  now %4d\n' "$kind" "$before" "$after"
  if [ "$kind" = "tsc" ] && [ -f "$base" ]; then
    regressions=$(join -t$'\t' -j1 -a2 -o 1.2,2.2,2.1 -e 0 <(sort -k1 "$base") <(sort -k1 "$now") \
      | awk -F'\t' '$3 > $2 {printf "  + %s: %s -> %s\n", $1, $2, $3}')
    if [ -n "$regressions" ]; then
      echo "$regressions"
      status=1
    fi
  fi
done

if [ "$status" -ne 0 ]; then
  echo
  echo "NEW errors introduced. Fix them, or record why in the spec."
else
  echo "no new errors against baseline"
fi
exit "$status"
