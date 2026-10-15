"""OP-B level-A placement check — OPi Zero 2W in the UMD cavity.

Run inside the keepout STEP context.  Results recorded in
docs/opb-placement-study.md.  All geometry REFERENCE_SCAN class except
the OPi envelope (VERIFIED outline + ESTIMATED component heights, U15).

Placement tested: OPi board 65x30, board at z 1.55..2.75 (cavity floor
median + board thickness), component envelope z 2.75..7.75, x 103..168,
y 24..54.
"""
import Import
import FreeCAD

Import.open('/home/placeless/dev/psp3000-internal-mod/cad/steps/psp3000_keepouts_refscan.step')
doc = FreeCAD.ActiveDocument

opi = doc.addObject("Part::Box", "opi_levelA")
opi.Length, opi.Width, opi.Height = 65.0, 30.0, 5.0
opi.Placement = FreeCAD.Placement(
    FreeCAD.Vector(103.0, 24.0, 2.75), FreeCAD.Rotation())
opi_board = doc.addObject("Part::Box", "opi_board")
opi_board.Length, opi_board.Width, opi_board.Height = 65.0, 30.0, 1.2
opi_board.Placement = FreeCAD.Placement(
    FreeCAD.Vector(103.0, 24.0, 1.55), FreeCAD.Rotation())
doc.recompute()

targets = []
cav = None
for o in doc.Objects:
    lbl = getattr(o, 'Label', '') or ''
    if lbl.startswith('boss_') or lbl == 'battery_bay':
        targets.append(o)
    if lbl == 'umd_cavity':
        cav = o

print('=== OP-B level-A interference check ===')
worst = None
for t in targets:
    d, pts, info = opi.Shape.distToShape(t.Shape)
    print('%s: %s' % (t.Label, 'INTERFERE' if d < 0.01 else 'CLEAR %.2fmm' % d))
    if worst is None or d < worst[1]:
        worst = (t.Label, d)

common = opi.Shape.common(cav.Shape)
pct = 100 * common.Volume / opi.Shape.Volume
print('inside cavity box: %.0f%%' % pct)
print('worst clearance: %s %.2fmm' % worst)
