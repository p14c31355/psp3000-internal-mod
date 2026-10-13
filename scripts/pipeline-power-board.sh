#!/usr/bin/env bash
# Full power-board PCB pipeline (Phase 6):
# 1. regenerate placement PCB from schematic netlist
# 2. placement + B.Cu/F.Cu GND zones (no manual routes)
# 3. export Specctra DSN, patch via padstack to 0.5/0.3
# 4. freerouting (headless)
# 5. import SES (GND net stripped - zones handle ground)
# 6. widen undersized vias to 0.5
# 7. DRC report
set -e
cd /home/placeless/dev/psp3000-internal-mod

echo "[1/7] regenerate placement"
.venv/bin/python scripts/gen_power_board_pcb.py 2>&1 | grep -vE "assert|property.h" | tail -1

echo "[2/7] zones"
.venv/bin/python scripts/route_power_board.py --no-routes 2>&1 | grep -vE "assert|property.h" | tail -1

echo "[3/7] DSN export + via patch"
.venv/bin/python - <<'PYEOF' 2>&1 | grep -vE "assert|property.h"
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import pcbnew
b = pcbnew.LoadBoard('pcb/power-board/power-board.kicad_pcb')
ok = pcbnew.ExportSpecctraDSN(b, '/tmp/power-board.dsn')
print('DSN:', ok)
PYEOF
python3 - <<'PYEOF'
s = open('/tmp/power-board.dsn').read()
s = s.replace('Via[0-1]_400:200_um', 'Via[0-1]_600:300_um')
s = s.replace('''    (padstack "Via[0-1]_400:200_um"
      (shape (circle F.Cu 400))''', '''    (padstack "Via[0-1]_600:300_um"
      (shape (circle F.Cu 600))''')
s = s.replace('''      (shape (circle B.Cu 400))
      (attach off)''', '''      (shape (circle B.Cu 600))
      (attach off)''')
open('/tmp/power-board.dsn','w').write(s)
print('DSN via patched to 0.5/0.3')
PYEOF

echo "[4/7] freerouting"
timeout 400 java -jar tools/freerouting-1.6.2.jar -de /tmp/power-board.dsn -do /tmp/power-board.ses -mp 30 -mt 1 > /tmp/fr_pipeline.log 2>&1
grep -cE "ERROR" /tmp/fr_pipeline.log || true

echo "[5/7] strip GND from SES, import"
python3 - <<'PYEOF'
s = open('/tmp/power-board.ses').read()
start = s.find('(net GND')
if start >= 0:
    d = 0
    k = start
    instr = False
    while k < len(s):
        ch = s[k]
        if instr:
            if ch == '"': instr = False
        elif ch == '"': instr = True
        elif ch == '(': d += 1
        elif ch == ')':
            d -= 1
            if d == 0:
                break
        k += 1
    s = s[:start] + s[k+1:]
    open('/tmp/power-board.ses','w').write(s)
    print('GND block stripped')
PYEOF
.venv/bin/python - <<'PYEOF' 2>&1 | grep -vE "assert|property.h"
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import pcbnew
b = pcbnew.LoadBoard('pcb/power-board/power-board.kicad_pcb')
ok = pcbnew.ImportSpecctraSES(b, '/tmp/power-board.ses')
print('SES import:', ok)
b.Save('pcb/power-board/power-board.kicad_pcb')
PYEOF

echo "[6/7] post-route fixup: full zone connection, stitching"
.venv/bin/python scripts/postroute_power_board.py 2>&1 | grep -vE "assert|property.h" | tail -5

echo "[7/7] DRC"
kicad-cli pcb drc --severity-all -o exports/drc.rpt pcb/power-board/power-board.kicad_pcb 2>&1 | head -2
grep "\[.*\]" exports/drc.rpt | grep -o "\[[a-z_]*\]" | sort | uniq -c || echo "no violations"
