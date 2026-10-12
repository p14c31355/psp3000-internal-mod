#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
echo "== KiCad CLI =="
kicad-cli --version
echo "== Git =="
git --version
echo "== Python =="
"$ROOT/.venv/bin/python" --version
echo "== KiCad Python =="
"$ROOT/.venv/bin/python" -c "import kipy; print(\"kicad-python / kipy OK\")"
echo "== FreeCAD =="
if command -v freecadcmd >/dev/null; then freecadcmd --version; elif command -v freecad >/dev/null; then freecad --version; else echo "FreeCAD not installed (optional for now)"; fi
echo "== Repository =="
git status --short
echo "KiCad/Hermes environment looks sane."
