"""SBC stacking feasibility probe (provisional, pre-donor-measurement).

Semantics (fixed 2026-10-13):
- body_envelope.step is the ALLOWED OUTER ENVELOPE (air space), not wall
  material. An SBC fully inside it must satisfy moved.cut(body) ~= 0.
- Collision with the provisional LCD module solid must satisfy
  moved.common(lcd) ~= 0.
- Height stack: board plane z0 chosen so header top (8.5) and underside
  (-4.5) stay inside 0..18.6: z0 in [4.5 .. 10.1]; we use z0 = 8.3.

This is a FEASIBILITY PROBE on placeholder geometry, NOT a fit claim.
Donor measurements U1-U3 gate any real placement freeze.

Run: freecadcmd cad/sbc_stack_probe.FCMacro (copy of this file inside repo).
"""
import os

import Part
from FreeCAD import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY = os.path.join(ROOT, "exports", "mech", "body_envelope.step")
LCD = os.path.join(ROOT, "exports", "mech", "lcd_module.step")
SBC = os.path.join(ROOT, "cad", "references", "radxa-zero3w",
                   "radxa_zero_3w_3d.stp")
OUT_DIR = os.path.join(ROOT, "exports", "mech")

Z0 = 8.3  # board plane height (bottom stays >= 3.8, top <= 16.8)


def transformed(sbc, dx, dy, angle):
    shape = sbc.copy()
    if angle:
        shape.rotate(Vector(0, 0, 0), Vector(0, 0, 1), angle)
    shape.translate(Vector(dx, dy, Z0))
    return shape


def probe(body, lcd, shape, tag):
    outside = shape.cut(body).Volume
    lcd_clash = shape.common(lcd).Volume
    bb = shape.BoundBox
    ok = outside < 0.01 and lcd_clash < 0.01
    status = "PASS" if ok else "FAIL"
    print(f"{tag}: outside={outside:8.3f} lcd_clash={lcd_clash:8.3f} "
          f"bbox X[{bb.XMin:6.1f},{bb.XMax:6.1f}] Y[{bb.YMin:5.1f},"
          f"{bb.YMax:5.1f}] -> {status}")
    return tag, outside, lcd_clash, status


def main():
    body = Part.read(BODY)
    lcd = Part.read(LCD)
    sbc = Part.read(SBC)

    # Official STEP occupies X 0..65, Y -1.5..30 (connector overhang at Y<0),
    # Z -4.5..8.5. Identity orientation: connectors face body-bottom (-Y).
    # +90 deg CCW: X becomes -30..1.5, Y becomes 0..65 (connectors face -X).
    # -90 deg CW: X becomes -1.5..30, Y becomes -65..0 (connectors face +X).
    cases = []
    # identity (connectors down): needs x0 >= 105 (past LCD) and x0+65<=169.4
    cases.append(("identity x0=104.4", 104.4, -1.5, 0))
    # rotated CCW (connectors toward -X/left): span X 31.5, Y 65
    for x0 in (135.0, 137.0):
        for y0 in (4.0, 6.0):
            cases.append((f"ccw x0={x0} y0={y0}", x0 + 30.0, y0, 90))
    # rotated CW (connectors toward +X/right): span X 31.5, Y 65
    for x0 in (135.0, 137.0):
        for y0 in (6.0, 8.0):
            cases.append((f"cw x0={x0} y0={y0}", x0 - 1.5, y0 + 65.0, -90))

    results = []
    for tag, dx, dy, ang in cases:
        results.append(probe(body, lcd, transformed(sbc, dx, dy, ang), tag))

    with open(os.path.join(OUT_DIR, "sbc_stack_probe.txt"), "w") as fh:
        fh.write("Radxa ZERO 3W stacking probe (PROVISIONAL geometry, "
                 "z0=%.1f)\n" % Z0)
        fh.write("outside = volume outside body envelope (want 0)\n")
        fh.write("lcd_clash = volume inside provisional LCD solid (want 0)\n\n")
        for tag, outside, clash, status in results:
            fh.write(f"{tag}: outside={outside:.3f} lcd_clash={clash:.3f} "
                     f"{status}\n")
        fh.write("\nNOTE: envelope-class result only; internal features "
                 "(walls, bosses, battery pocket, UMD door) pending U1-U3.\n")


main()
