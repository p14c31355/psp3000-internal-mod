# UMD cavity cut study v1 — human-cutter-friendly cut plan

Updated: 2026-10-15.  Class: REFERENCE_SCAN (BitBuilt scan geometry)
+ user-authorized cutting (UMD-mechanism-only structures; protected:
perimeter, screw bosses, hinge/latch, speaker mounts, structural
ribs, battery structure).

## What this study produced

- `cad/cut_study_v1.py` — extracts the rib/web material inside the
  cavity walls from the aligned scan zmap (1 mm), excludes boss
  disks (+2 mm) and the perimeter walls, and segments the remaining
  cuttable web into **straight 4 mm-tall rectangular pockets**.
- `cad/steps/umd_cut_study_v1.step` — the 17 cut-pocket solids + the
  OPi level-A envelope, in body coordinates.
- `exports/umd-cut-study-v1.svg` — the top-view cut map (red = cut
  pockets, blue = OPi envelope, dash = cavity outline).

## The cut list (17 pockets, all 7.7 mm deep)

Every pocket: cut from the cavity's inner surface down to the floor
level (z 1.0), i.e. **remove ~7.7 mm of web** in the red areas of the
SVG.  Straight edges are deliberate: a rotary tool with a straight
guide (or a small flat file) can follow them; 4 mm band height fits a
3 mm burr with room.

Grouped for actual cutting (adjacent bands merge into taller cuts):

| Zone | X span (mm) | Y span (mm) | Notes |
|---|---|---|---|
| A (upper) | 121..165 | 16..35 | five 4mm bands merge → one 20mm-tall cut |
| B (right column) | 158..164 | 8..15 | two bands near the right wall |
| C (mid) | 128..165 | 36..39 | single band |
| D (lower) | 121..163 | 40..63 | six bands merge → 24mm-tall cut |
| E (bottom) | 122..138 | 64..67 | single band above the rear wall |

Protected (do NOT cut): the 3 boss disks inside the ROI (x 119/127/149,
y 1.6/2/10.2 + 2 mm margin), the y ≥ 66 rear wall band, the x ≥ 166
side wall, and everything outside the dashed cavity outline.

## Depth stops for the human pass

- Floor target: z 1.0 (the disc-well floor level).  Measure from the
  cavity's current inner surface: remove **7.7 mm** max — mark the
  burr with tape at 7.7 mm as a depth stop, or cut to a straightedge
  laid across the rim (rim z 8.73 → floor 1.0).
- Work slowly at the boss margins — 2 mm buffer only.
- After cutting: deburr, then re-photograph the cavity for the
  as-cut zmap update.

## What v1 does NOT include (honest limits)

- The rib zmap is a 1 mm grid top-view; undercuts and thin vertical
  webs that don't reach the top plane are invisible to it.  The real
  structure may need less (or more) cutting than mapped — the
  as-cut re-scan/re-photo closes this.
- The OPi level-A placement (65×30 at x 103..168) needs the 14 mm
  overhang region cleared too — that region's occupancy is the main
  board shield stack (photo-ESTIMATED), still not a keepout solid.
- Boss positions come from the 3rd-party scan; OUR unit may differ —
  verify each boss with the pin-gauge/photo before the final pass.

## Next

1. Add the main-board envelope (from the teardown photos, ESTIMATED)
   as a keepout and re-run the OP-B check.
2. As-cut photo round → update zmap → v2 pocket list (if needed).
