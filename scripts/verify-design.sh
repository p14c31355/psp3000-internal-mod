#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
branch="$(git branch --show-current)"
[[ -n "$branch" && "$branch" != main ]] || { echo "Refusing verification on main or detached HEAD" >&2; exit 2; }
schematic= board= enclosure=
while (($#)); do
  case "$1" in
    --schematic|--board|--enclosure)
      (($# >= 2)) || { echo "Missing value for $1" >&2; exit 2; }
      case "$1" in
        --schematic) schematic="$2";;
        --board) board="$2";;
        --enclosure) enclosure="$2";;
      esac
      shift 2;;
    *) echo "Unknown argument: $1" >&2; exit 2;;
  esac
done
[[ -n "$schematic" || -n "$board" ]] || { echo "Supply --schematic and/or --board" >&2; exit 2; }
[[ -z "$board" || -n "$schematic" ]] || { echo "PCB verification requires --schematic for ERC" >&2; exit 3; }
[[ -z "$enclosure" || -n "$board" ]] || { echo "--enclosure requires --board" >&2; exit 2; }
command -v kicad-cli >/dev/null || { echo "kicad-cli missing" >&2; exit 2; }
mkdir -p exports
if [[ -n "$schematic" ]]; then
  [[ -f "$schematic" ]] || { echo "Schematic missing: $schematic" >&2; exit 2; }
  kicad-cli sch erc --exit-code-violations --severity-all -o exports/erc.rpt "$schematic"
fi
if [[ -n "$board" ]]; then
  [[ -f "$board" ]] || { echo "Board missing: $board" >&2; exit 2; }
  kicad-cli pcb drc --exit-code-violations --severity-all -o exports/drc.rpt "$board"
  kicad-cli pcb export step --force -o exports/board.step "$board"
  [[ -s exports/board.step ]] || { echo "STEP export missing or empty" >&2; exit 1; }
  if [[ -n "$enclosure" ]]; then
    [[ -f "$enclosure" ]] || { echo "Enclosure missing: $enclosure" >&2; exit 2; }
    scripts/check-interference.sh exports/board.step "$enclosure"
  else
    echo "Mechanical interference: BLOCKED (provide measured, aligned enclosure solid)" >&2
    exit 3
  fi
fi
git diff --check
git status --short
git diff --stat
echo "Review the full git diff and generated reports before committing."
