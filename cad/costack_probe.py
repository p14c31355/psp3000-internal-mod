"""SBC + power-board co-stacking probe (Phase 7 co-design loop).

Semantics (fixed 2026-10-13):
- body_envelope.step is the ALLOWED OUTER ENVELOPE (air), not walls.
- lcd_module.step is the provisional LCD solid.
- Radxa ZERO 3W placement uses the PASS cases from sbc_stack_probe
  (90-degree rotation, x0=135, y0=4..6, z0=8.3).
- Power board is simulated as a 48 x 36 mm outline (the largest
  rectangle inside the DERIVED 60 mm UMD disc cavity), placed in the
  UMD cavity zone: the stock UMD drive sits inboard of the right shell
  half, so the cavity center is provisionally placed at the body's
  right-center.  The cavity X/Y position is UNKNOWN (U2); the probe
  sweeps plausible positions and reports which ones avoid the Radxa,
  the LCD, and the body envelope.

This is a FEASIBILITY PROBE on placeholder geometry, NOT a fit claim.
U2 (cavity extent) and U1-U3 (bosses, walls) gate any placement freeze.

Run: freecadcmd cad/costack_probe.FCMacro (copy inside repo).
"""
import os

import Part
from FreeCAD import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY = os.path.join(ROOT, "exports", "mech", "body_envelope.step")
LCD = os.path.join(ROOT, "exports", "mech", "lcd_module.step")
SBC = os.path.join(ROOT, "cad", "references", "radxa-zero3w",
                   "radxa_zero_3w_3d.stp")

Z0_SBC = 9.5
# Power board: 48 x 36 x 1.6 mm (2-layer, no tall parts on top except
# the USB-C shell ~3.2 mm and the inductor ~2 mm).
PB_W, PB_D, PB_T = 48.0, 36.0, 1.6
Z0_PB = 1.0  # bottom of stack, USB-C top 4.2 < SBC underside 5.0


def box(dx, dy, dz, x0, y0, z0):
    return Part.makeBox(dx, dy, dz, Vector(x0, y0, z0))


def report(tag, shape, body, lcd, sbc):
    outside = shape.cut(body).Volume
    lcd_clash = shape.common(lcd).Volume
    sbc_clash = shape.common(sbc).Volume
    bb = shape.BoundBox
    ok = outside < 0.01 and lcd_clash < 0.01 and sbc_clash < 0.01
    status = "PASS" if ok else "FAIL"
    print(f"{tag}: out={outside:7.1f} lcd={lcd_clash:6.1f} "
          f"sbc={sbc_clash:6.1f} X[{bb.XMin:5.1f},{bb.XMax:6.1f}] "
          f"Y[{bb.YMin:5.1f},{bb.YMax:5.1f}] -> {status}")
    return status


def main():
    body = Part.read(BODY)
    lcd = Part.read(LCD)
    sbc = Part.read(SBC)

    # Radxa at the proven PASS spot: 90 deg CCW, x0=135, y0=6, z0=8.3.
    # The official STEP occupies X 0..65, Y -1.5..30 at identity; +90 CCW
    # puts it at X -30..1.5, Y 0..65 relative to its origin, so we
    # translate to x0=135+1.5?  sbc_stack_probe already solved this:
    # replicate its transform exactly (rotate 90 about origin, translate
    # (135, 6, 8.3)).
    sbc_moved = sbc.copy()
    sbc_moved.rotate(Vector(0, 0, 0), Vector(0, 0, 1), 90)
    sbc_moved.translate(Vector(135, 6, Z0_SBC))
    report("SBC (ccw x0=135 y0=6)", sbc_moved, body, lcd, sbc.copy())

    # Power board sweep inside the right half of the body, below the
    # SBC plane.  The body is 169.4 x 71.4; the right-center zone
    # (UMD cavity, provisional) is around X 100..160, Y 8..62.
    print()
    best = None
    for x0 in (100, 110, 118):
        for y0 in (10, 20, 30):
            pb = box(PB_W, PB_D, PB_T, x0, y0, Z0_PB)
            status = report(f"PB board @({x0},{y0})", pb, body, lcd, sbc_moved)
            if status == "PASS" and best is None:
                best = (x0, y0)
    # The chosen PB with its tallest top-side part (USB-C shell 3.2 mm)
    # as a separate solid on top of the board plane.
    if best:
        x0, y0 = best
        usbc = box(9.0, 7.5, 3.2, x0 + 2.0, y0 + 2.0, Z0_PB + PB_T)
        report(f"PB+USBC @({x0},{y0}) board@z{Z0_PB} usbc_top="
               f"{Z0_PB + PB_T + 3.2:.1f} vs SBC under "
               f"{Z0_SBC - 4.5:.1f}", usbc, body, lcd, sbc_moved)


main()
