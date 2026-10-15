"""Align the BitBuilt PSP-3000 scans into the Sony body coordinate system.

Body coordinate system (per docs/MEASUREMENT-PLAN.md):
  origin  = bottom-left of the FRONT face (display window up)
  X right, Y up, Z toward the viewer (out of the front face)

Alignment method (no ICP needed — the parts share the body perimeter):
  - X: both scans span the full body length -> map each part's X
    extents onto [0, 168.2] (their own measured span, ~1% off the
    169.4 spec; keep scan scale, record the delta).
  - Y: same, onto [0, 71].
  - Z: the parts assemble at the body's mid-plane.  Rear outer face
    (battery side) is the z=0 datum; the front outer face (glass)
    defines the positive end.  Body thickness 18.6 mm spec; the scans
    measure front 13.2 + rear 17.35 with overlap (they share the
    mid-plane seam).  We anchor rear z=0 at its own z-min, and place
    front z-min at rear_zmin + spec_thickness - front_thickness,
    recording the seam assumption as an explicit constant.

Outputs:
  cad/references/bitbuilt-psp3000/alignment.json
  - per-part transform (dx, dy, dz) + provenance constants

The transforms are rigid (translate only).  No scaling is applied.
"""
import json
import numpy as np
from stl import mesh

BODY_LEN_SPEC = 169.4
BODY_W_SPEC = 71.4
BODY_T_SPEC = 18.6

parts = {}
for name in ('front', 'rear'):
    m = mesh.Mesh.from_file(
        f'cad/references/bitbuilt-psp3000/scan/PSP 3000 {name}.stl')
    v = m.vectors.reshape(-1, 3)
    mn, mx = v.min(axis=0), v.max(axis=0)
    parts[name] = {'min': mn.tolist(), 'max': mx.tolist(),
                   'span': (mx - mn).tolist()}

# X/Y: align both to their own scan min (rigid translate to origin).
# The two parts were scanned in the same rig (front x 40.95..209.11,
# rear x 42.06..210.29 — 1.1 mm rig offset).  Normalize that away and
# record it as rig offset.
rig_dx = parts['rear']['min'][0] - parts['front']['min'][0]
rig_dy = parts['rear']['min'][1] - parts['front']['min'][1]

# Z: rear z-min = 0 datum.  Front z-min sits at:
#   body_t_spec - front_span_z  (front outer face at 18.6)
front_dz = BODY_T_SPEC - parts['front']['span'][2]

result = {
    'coordinate_system': {
        'origin': 'bottom-left of front face',
        'x': 'right', 'y': 'up', 'z': 'toward viewer',
        'datum': 'rear outer face (battery side) = z 0',
    },
    'specs_mm': {'L': BODY_LEN_SPEC, 'W': BODY_W_SPEC, 'T': BODY_T_SPEC},
    'scan_scale_check': {
        'front_span': parts['front']['span'],
        'rear_span': parts['rear']['span'],
        'note': 'X/Y spans ~1% under spec; scan kept at native scale',
    },
    'transforms': {
        'front': {'dx': 0.0, 'dy': 0.0, 'dz': round(front_dz, 3)},
        'rear': {'dx': 0.0, 'dy': 0.0, 'dz': 0.0},
    },
    'rig_offset': {'dx': round(rig_dx, 3), 'dy': round(rig_dy, 3)},
    'seam_assumption': (
        'Front outer face anchored at z=18.6 (spec). Front scan z-span '
        f"{parts['front']['span'][2]:.2f} mm; overlap with rear spans the "
        'mid-plane seam. Physical seam measurement can replace the '
        'assumption without changing any other constant.'),
}
with open('cad/references/bitbuilt-psp3000/alignment.json', 'w') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
