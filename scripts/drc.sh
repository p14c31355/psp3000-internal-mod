#!/usr/bin/env bash
set -euo pipefail
BOARD="${1:-$(find pcb -maxdepth 1 -name "*.kicad_pcb" | head -n1)}"
[ -n "$BOARD" ] || { echo "No .kicad_pcb found in pcb/"; exit 1; }
mkdir -p exports
kicad-cli pcb drc --exit-code-violations --output exports/drc.rpt "$BOARD"
cat exports/drc.rpt
