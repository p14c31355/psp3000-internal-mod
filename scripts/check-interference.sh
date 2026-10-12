#!/usr/bin/env bash
set -euo pipefail
[[ $# -eq 2 ]] || { echo "Usage: $0 board.step enclosure-solid.step" >&2; exit 2; }
[[ -s "$1" && -s "$2" ]] || { echo "Both STEP files must exist and be nonempty" >&2; exit 2; }
command -v freecadcmd >/dev/null || { echo "freecadcmd missing" >&2; exit 2; }
ROOT="$(git rev-parse --show-toplevel)"
mkdir -p "$ROOT/exports"
export BOARD_STEP="$(realpath "$1")" ENCLOSURE_STEP="$(realpath "$2")" INTERFERENCE_REPORT="$ROOT/exports/interference.txt"
rm -f "$INTERFERENCE_REPORT"
freecadcmd "$ROOT/scripts/check-interference.FCMacro"
[[ -s "$INTERFERENCE_REPORT" ]] || { echo "FreeCAD produced no interference report" >&2; exit 1; }
cat "$INTERFERENCE_REPORT"
grep -q '^RESULT: PASS$' "$INTERFERENCE_REPORT"
