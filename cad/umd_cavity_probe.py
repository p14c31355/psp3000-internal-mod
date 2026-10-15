"""UMD cavity usable-volume probe — BitBuilt scan (REFERENCE_SCAN class).

Extracts the UMD-bay cavity geometry from the aligned rear-shell scan
and reports the usable free volume for the v2 OP-B placement.

Method: 1 mm XY grid Zmax top-map of the rear mesh (battery-side up).
The cavity is where the map is DEEP (the disc-well floor is visible
from the battery side through the removed drive).  Rims around it
read z 7.7-9.9 mm; the deep visible floor band reads z 1.1-3.5 mm.

Outputs a structured summary + the cavity floor mask as JSON for the
FreeCAD keepout build.
"""
import json
import numpy as np
import math

zmax = np.load('/tmp/rear_zmax1.npy')  # body coords, 1mm grid, 169x71

# The cavity band (from the profile): y 12..66, x 115..169
Y0, Y1, X0, X1 = 12, 67, 115, 169
sub = zmax[Y0:Y1, X0:X1]
deep = sub < 5.0
ys, xs = np.where(deep)
x0, x1 = int(xs.min() + X0), int(xs.max() + X0)
y0, y1 = int(ys.min() + Y0), int(ys.max() + Y0)
w, h = x1 - x0, y1 - y0
area = int(deep.sum())
eq_d = 2 * math.sqrt(area / math.pi)
cx, cy = float((xs + X0).mean()), float((ys + Y0).mean())
deep_z = sub[deep]
rim = sub[(sub >= 7.0) & (sub < 10.5)]

out = {
    'class': 'REFERENCE_SCAN',
    'source': 'BitBuilt PSP 3000 rear.stl, body coords (1mm grid zmax)',
    'cavity_opening_visible': {
        'x_mm': [x0, x1], 'y_mm': [y0, y1],
        'width_mm': w, 'height_mm': h,
        'area_mm2': area,
        'equivalent_circle_diameter_mm': round(eq_d, 1),
        'centroid_mm': [round(cx, 1), round(cy, 1)],
    },
    'floor_z_visible': {
        'p10': round(float(np.percentile(deep_z, 10)), 2),
        'median': round(float(np.median(deep_z)), 2),
        'p90': round(float(np.percentile(deep_z, 90)), 2),
    },
    'rim_z': {
        'median': round(float(np.median(rim)), 2) if rim.size else None,
        'note': 'cavity wall top band, z 7.7-9.9 mm',
    },
    'interpretation': (
        'The deep-visible opening is the region where the disc-well '
        'floor is seen from the battery side. The full cavity is '
        'larger in X than the visible band (the drive well extends '
        'under the door trough on the door side); the owner-directed '
        'cut study must add the door-trough region from the front/UMD '
        'lid scans before declaring the usable volume.'),
    'body_thickness_datum': 'rear outer face = z 0',
}
with open('cad/references/bitbuilt-psp3000/umd-cavity-probe.json', 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
