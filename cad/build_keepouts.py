"""Keepout solids from the BitBuilt scans (REFERENCE_SCAN class).

Builds simplified FreeCAD keepout volumes for the v2 mechanical study
and exports them as STEP for the interference workflow:

- screw bosses: cylinders at the 9 cluster centers (z > 16 mm, d from
  the raster cluster width + 1 mm margin), height = boss z
- battery bay: box from the photo/scan bay region
- UMD cavity: box at the deep-region footprint, floor at z=1.0 (the
  visible-floor median), walls to the rim median z=8.73
- glass datum plane: front side, z = 18.6 - 2.5 (glass outer profile
  2.2-2.8 mm) as a reference box above the display window band

These are PLANNING keepouts (coarse boxes/cylinders), not OEM replicas.
"""
import json
import numpy as np

BOSSES = [
    {'x': 31.1, 'y': 61.9, 'z': 17.0, 'd': 13},
    {'x': 31.0, 'y': 46.0, 'z': 16.98, 'd': 5},
    {'x': 29.3, 'y': 53.0, 'z': 16.54, 'd': 3},
    {'x': 18.3, 'y': 9.7, 'z': 16.47, 'd': 2},
    {'x': 47.0, 'y': 1.5, 'z': 16.29, 'd': 7},
    {'x': 127.0, 'y': 2.0, 'z': 16.24, 'd': 3},
    {'x': 119.1, 'y': 1.6, 'z': 16.08, 'd': 9},
    {'x': 149.0, 'y': 10.2, 'z': 16.08, 'd': 3},
    {'x': 23.4, 'y': 60.7, 'z': 16.08, 'd': 4},
]

import FreeCAD as App
import Part

doc = App.newDocument("keepouts")

# --- screw bosses (cylinders, full height from floor to boss top) ---
for i, b in enumerate(BOSSES):
    c = doc.addObject("Part::Cylinder", f"boss_{i}")
    c.Radius = b['d'] / 2.0
    c.Height = b['z']
    c.Placement = App.Placement(
        App.Vector(b['x'] - b['d'] / 2.0, b['y'] - b['d'] / 2.0, 0.0),
        App.Rotation())

# --- battery bay (from photo analysis: bay at left, contacts at the
#     bay's upper edge; footprint approximated from the scan low band
#     y 2..12 around x 0..60 plus depth to the rim) ---
bay = doc.addObject("Part::Box", "battery_bay")
bay.Length, bay.Width, bay.Height = 60.0, 34.0, 8.7
bay.Placement = App.Placement(App.Vector(0.0, 0.0, 0.0), App.Rotation())

# --- UMD cavity (main opening + trough extension footprint) ---
cav = doc.addObject("Part::Box", "umd_cavity")
cav.Length, cav.Width, cav.Height = 51.0, 56.0, 8.7
cav.Placement = App.Placement(App.Vector(117.0, 8.0, 0.0), App.Rotation())

# --- glass datum (front side, reference band over the window) ---
glass = doc.addObject("Part::Box", "glass_datum")
glass.Length, glass.Width, glass.Height = 104.0, 50.0, 2.5
glass.Placement = App.Placement(App.Vector(32.0, 10.0, 16.1), App.Rotation())

doc.recompute()

import Import
Import.export([o for o in doc.Objects],
              "cad/steps/psp3000_keepouts_refscan.step")
print("exported cad/steps/psp3000_keepouts_refscan.step")
print(f"bosses: {len(BOSSES)}, bay 60x34x8.7 @ (0,0), cavity 51x56x8.7 @ (117,8), "
      f"glass datum 104x50x2.5 @ (32,10,16.1)")
