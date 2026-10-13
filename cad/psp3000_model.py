"""PSP-3000 mechanical constraint model builder (headless, reproducible).

Consumes cad/params.md provenance-tagged values and emits STEP exports:
  exports/mech/body_envelope.step   - outer silhouette prism (VPS dims)
  exports/mech/lcd_module.step      - Sharp LQ043T3LX02 panel (VPS dims)
  exports/mech/keepout_blocks.step  - per-region keepout volumes
UNKNOWN/ESTIMATED inputs are rendered with explicitly flagged placeholder
volumes; they are not manufacturing constraints.

Run:  freecadcmd cad/psp3000_model.py   (or .FCMacro copy)
"""
import math
import os
import re
import sys

import Part
from FreeCAD import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "exports", "mech")


def load_params(path):
    """Parse cad/params.md table rows -> {name: (value_str, class)}."""
    params = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^([A-Z0-9_]+)\s*\|\s*([^|]+?)\s*\|\s*"
                         r"(VPS|VRS|MEASURED|DERIVED|ESTIMATED|UNKNOWN)\s*\|",
                         line)
            if m:
                params[m.group(1)] = (m.group(2).strip(), m.group(3))
    return params


def fnum(params, name):
    value, cls = params[name]
    if cls == "UNKNOWN":
        raise ValueError(f"{name} is UNKNOWN - refusing to use a nominal")
    return float(value), cls


def rounded_rect_prism(w, d, h, r):
    """Prism of a rounded rectangle, W x D in XY, height h in +Z."""
    r = min(r, w / 2.0 - 0.01, d / 2.0 - 0.01)
    face_pts = [
        Vector(r, 0, 0), Vector(w - r, 0, 0), Vector(w, r, 0),
        Vector(w, d - r, 0), Vector(w - r, d, 0), Vector(r, d, 0),
        Vector(0, d - r, 0), Vector(0, r, 0),
    ]
    edges = []
    n = len(face_pts)
    # corner arc centers, paired with odd (arc) edges in face_pts order
    centers = [
        Vector(w - r, r, 0),      # bottom-right: (w-r,0) -> (w,r)
        Vector(w - r, d - r, 0),  # top-right:    (w,r)  -> (w-r,d)
        Vector(r, d - r, 0),      # top-left:     (r,d)  -> (0,d-r)
        Vector(r, r, 0),          # bottom-left:  (0,r)  -> (r,0)
    ]
    for i in range(n):
        a, b = face_pts[i], face_pts[(i + 1) % n]
        if i % 2 == 1:
            c = centers[(i - 1) // 2]
            sa = (a - c).normalize()
            sb = (b - c).normalize()
            mid = c + (sa + sb).normalize().multiply(r)
            edges.append(Part.Arc(a, mid, b).toShape())
        else:
            edges.append(Part.LineSegment(a, b).toShape())
    wire = Part.Wire(Part.__sortEdges__(edges))
    face = Part.Face(wire)
    return face.extrude(Vector(0, 0, h))


def box(x, y, z, w, d, h):
    return Part.makeBox(w, d, h, Vector(x, y, z))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    params = load_params(os.path.join(ROOT, "cad", "params.md"))

    body_w, body_w_cls = fnum(params, "BODY_W")
    body_d, body_d_cls = fnum(params, "BODY_D")
    body_h, body_h_cls = fnum(params, "BODY_H")
    corner_r, corner_cls = fnum(params, "BODY_CORNER_R")

    solids = {}
    notes = []

    # Body envelope (outer silhouette prism). Corner radius is ESTIMATED:
    # flagged, refined later from donor photos.
    body = rounded_rect_prism(body_w, body_d, body_h, corner_r)
    solids["body_envelope"] = body
    notes.append(f"body_envelope: {body_w}x{body_d}x{body_h} "
                 f"corner_r={corner_r}({corner_cls})")

    # LCD module PROVISIONAL placement: module flush toward the LEFT edge
    # (screen occupies the left portion in landscape; controls on the right)
    # and vertically centered. Flagged; real position comes from m1.6.
    lcd_w, _ = fnum(params, "LCD_W")
    lcd_h, _ = fnum(params, "LCD_H")
    lcd_t, _ = fnum(params, "LCD_T")
    if params["LCD_X"][1] == "UNKNOWN" or params["LCD_Y"][1] == "UNKNOWN":
        lx = 1.2
        ly = (body_d - lcd_h) / 2.0
        notes.append(f"lcd_module position PROVISIONAL (LCD_X/Y UNKNOWN): "
                     f"placed at x={lx:.2f} y={ly:.2f} (left-flush, "
                     f"v-centered)")
    else:
        lx = fnum(params, "LCD_X")[0]
        ly = fnum(params, "LCD_Y")[0]
    lcd = box(lx, ly, 0.0, lcd_w, lcd_h, lcd_t)
    solids["lcd_module"] = lcd

    # Keepout: regions whose height budgets are UNKNOWN get explicit
    # "investigation" marker boxes at zero-height footprint on Z=0 plane
    # (footprints only, no volume claims).
    footprints = {
        "kp_mainboard_region": box(60.0, 0.0, 0.0, 70.0, 30.0, 0.01),
        "kp_battery_region": box(8.0, 0.0, 0.0, 60.0, 36.0, 0.01),
        "kp_umd_cavity": box(60.0, 30.0, 0.0, 70.0, 30.0, 0.01),
    }
    notes.append("keepout footprints are PLACEHOLDER regions pending U1-U3 "
                 "measurements; heights intentionally zero")
    for name, solid in footprints.items():
        solid.exportStep(os.path.join(OUT_DIR, name + ".step"))

    for name, solid in solids.items():
        solid.exportStep(os.path.join(OUT_DIR, name + ".step"))

    report = ["PSP-3000 mechanical model build report", ""] + notes
    report.append("")
    report.append(f"Exported {len(solids) + len(footprints)} STEP files "
                  f"to {OUT_DIR}")
    with open(os.path.join(OUT_DIR, "build_report.txt"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    print("\n".join(report))


main()
