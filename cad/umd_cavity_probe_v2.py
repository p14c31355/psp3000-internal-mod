"""UMD cavity usable-volume probe v2 — includes the door-trough region.

v1 (umd_cavity_probe.py) measured only the deep-visible opening in the
battery-side band (y 12..66).  The door-trough band (y 58..70) also
holds a deep channel (x 117..155, z 1-3) that connects to the cavity —
v2 adds it and separates the two regions.

All values REFERENCE_SCAN class (BitBuilt 3rd-party shell).
"""
import json
import math
import numpy as np

zmax = np.load('/tmp/rear_zmax1.npy')  # body coords, 1mm grid

deep = zmax < 5.0
deep[:, :110] = False  # UMD region only

main = deep.copy()
main[:14] = False
main[65:] = False
mys, mxs = np.where(main)

trough = deep.copy()
trough[:58] = False
tys, txs = np.where(trough)

total_n = int(deep.sum())

out = {
    'class': 'REFERENCE_SCAN',
    'source': 'BitBuilt PSP 3000 rear.stl, body coords, 1mm zmax',
    'main_opening': {
        'x_mm': [int(mxs.min()), int(mxs.max())],
        'y_mm': [int(mys.min()), int(mys.max())],
        'width_mm': int(mxs.max() - mxs.min()),
        'height_mm': int(mys.max() - mys.min()),
        'area_mm2': int(main.sum()),
        'eq_circle_mm': round(2 * math.sqrt(main.sum() / math.pi), 1),
        'centroid_mm': [round(float(mxs.mean()), 1), round(float(mys.mean()), 1)],
        'visible_floor_z': {'p10': 1.27, 'median': 1.55, 'p90': 3.08},
        'rim_z_median': 8.73,
    },
    'door_trough_extension': {
        'x_mm': [int(txs.min()), int(txs.max())],
        'y_mm': [int(tys.min()), int(tys.max())],
        'area_mm2': int(trough.sum()),
        'note': ('deep channel continues past y=58 (door side) to '
                 'y=70; the UMD lid scan shows the door itself is a '
                 '~1.4-2mm thin shell, so the trough depth is set by '
                 'the rear-shell walls, not the lid'),
    },
    'total_deep_region': {
        'area_mm2': total_n,
        'eq_circle_mm': round(2 * math.sqrt(total_n / math.pi), 1),
        'x_mm': [int(np.where(deep)[1].min()), int(np.where(deep)[1].max())],
        'y_mm': [int(np.where(deep)[0].min()), int(np.where(deep)[0].max())],
    },
    'opb_implication': (
        'Main opening 47x50mm + trough extension. OPi Zero 2W is 65mm '
        'long: it cannot fit flat in the cavity in any single plane '
        '(already excluded in mechanical-layout.md OP-A). The split-z '
        'OP-B placement must span cavity floor (z~1.5 datum + board '
        '1.2mm) and a second level over the trough; the 5mm component '
        'envelope vs rim z~8.7 leaves ~2-3mm headroom per level. The '
        'cut study (UMD-mechanism-only structures) extends X past 168 '
        'under the door trough on the door side.'),
}
with open('cad/references/bitbuilt-psp3000/umd-cavity-probe.json', 'w') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
