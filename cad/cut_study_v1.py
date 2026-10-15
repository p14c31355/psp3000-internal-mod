"""Cut study v1 — UMD-mechanism-only material removal, human-friendly.

Goal: compute the usable cavity after cutting UMD-mechanism-only
structures, and produce cutter-friendly guidance (flat pockets, guide
planes, depth stops — a human with a rotary tool can follow them).

Method (REFERENCE_SCAN class throughout):
  1. Load the aligned rear-shell scan zmap (1mm grid, body coords).
  2. Define the cut envelope: the cavity footprint (main opening +
     trough) minus protected keepouts (bosses + 2mm margin).
  3. Cut depth: everything between the cavity floor (z 1.0) and the
     rim band (z 8.73) that is UMD-mechanism structure.  In this scan
     the floor is already open at the insert axis (user-measured 40mm
     span), so the cut targets are the ribs/grid inside the walls.
  4. Human-friendly cut volumes: the rib grid between cells becomes
     straight-edged rectangular pockets (a rotary tool with a guide
     edge can follow them); each pocket gets a depth number.

Outputs:
  - cad/steps/umd_cut_study_v1.step (cut envelope + keepouts +
    OPi envelope for visual assembly)
  - /tmp/cut_pockets.json (machine-readable pocket list)
  - prints a human cut plan
"""
import json
import numpy as np

zmax = np.load('/tmp/rear_zmax1.npy')  # body coords, 1mm, 169x71

# --- region of interest: cavity footprint (main + trough) ---
X0, X1 = 115, 169   # scan showed deep region x 117..168
Y0, Y1 = 8, 71      # main y 14..64 + trough y 58..70 + margin

sub = zmax[Y0:Y1, X0:X1]

# keepouts: bosses (from build_keepouts.py, +2mm margin)
BOSSES = [
    (127.0, 2.0), (119.1, 1.6), (149.0, 10.2),
]
# only bosses inside the ROI matter; also protect the y>=66 perimeter
# band (rear wall) and x>=166 (side wall).

rim_z = 8.73
floor_z = 1.0

# rib grid = cells where zmax is between floor and rim - 2 (the web
# material inside the cavity walls).  Protected: boss disks + walls.
rib = (sub >= floor_z) & (sub < rim_z - 2.0) & ~np.isnan(sub)

# zero out boss disks (+2mm):
yy, xx = np.mgrid[Y0:Y1, X0:X1]
for bx, by in BOSSES:
    disk = ((xx - bx) ** 2 + (yy - by) ** 2) <= 7.0 ** 2  # ~5mm boss + 2mm
    rib &= ~disk

# zero the perimeter walls:
rib &= (yy < 66) & (xx < 166)

ys, xs = np.where(rib)
if len(ys):
    print("rib cells: n=%d" % len(ys))
    print("x %d..%d, y %d..%d" % (xs.min()+X0, xs.max()+X0, ys.min()+Y0, ys.max()+Y0))
    # cluster into straight-edged pockets (greedy row bands):
    # quantize to 4mm rows for tool-friendly straight cuts
    bands = {}
    for y, x in zip(ys, xs):
        band = (y // 4) * 4
        bands.setdefault(band, []).append(x)
    pockets = []
    for band, xlist in sorted(bands.items()):
        xlist = sorted(set(xlist))
        # split into runs (gaps > 3mm start a new pocket)
        runs = []
        start = prev = xlist[0]
        for x in xlist[1:]:
            if x - prev > 3:
                runs.append((start, prev))
                start = x
            prev = x
        runs.append((start, prev))
        for a, b in runs:
            if b - a >= 4:
                pockets.append({
                    'x0': int(a + X0), 'x1': int(b + X0),
                    'y0': int(band + Y0), 'y1': int(band + Y0 + 3),
                    'cut_depth_mm': round(float(rim_z - floor_z), 2),
                })
    print("tool-friendly straight pockets (4mm tall bands, >=4mm long):")
    for p in pockets:
        print("  x %d..%d, y %d..%d, depth %.1fmm (floor z=%.1f)"
              % (p['x0'], p['x1'], p['y0'], p['y1'],
                 p['cut_depth_mm'], floor_z))
    with open('/tmp/cut_pockets.json', 'w') as f:
        json.dump({'rim_z': rim_z, 'floor_z': floor_z,
                   'pockets': pockets}, f, indent=2)
else:
    print("no rib cells found in ROI")
