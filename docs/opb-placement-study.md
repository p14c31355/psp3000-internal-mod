# OP-B placement study — OPi Zero 2W in the UMD cavity

Updated: 2026-10-15.  Class: geometry REFERENCE_SCAN + OPi envelope
(VERIFIED outline 65×30×1.2, component heights ESTIMATED 5.0/1.5 mm,
U15 pending).  Tooling: `cad/opb_placement_check.py` against the
keepout STEP (`cad/steps/psp3000_keepouts_refscan.step`).

## Level-A test result (first FreeCAD interference check of v2)

Placement: OPi board 65×30 at z 1.55..2.75 (cavity floor median +
board), components to z 7.75, x 103..168, y 24..54.

| Keepout | Clearance |
|---|---|
| boss_0..boss_8 (all 9) | CLEAR, worst **boss_7 = 13.80 mm** |
| battery_bay | CLEAR 43.00 mm |
| inside cavity box | 78% of the OPi volume |

**Interpretation:** OP-B level A clears every boss and the battery bay
in the current keepout set.  78% of the OPi sits inside the cavity
box; the remaining 22% is the 14 mm x-overhang at x 103..117, which
leaves the cavity on the battery-bay side.  That overhang region's
occupancy (main board shield stack vs free air) is the open question —
the photo analysis shows the MB under the cavity floor at that side,
but the MB's top surface height there is not yet measured (U16-adjacent
photo ask).

## Headroom arithmetic (level A)

- floor median z 1.55 + board 1.2 + components 5.0 = top 7.75
- rim median 8.73 → **0.98 mm headroom** at the component envelope
  top — TIGHT.  If U15 (OPi as-measured component height) exceeds
  5.0 mm, level A fails at the rim; the fallback is sinking the board
  to the floor minimum (z 1.27 → top 7.47 → 1.26 mm headroom) or
  cutting UMD-only plastic under the rim.

## Not yet included (honest limits)

- Door-trough z-ceiling: the trough extension is in the footprint but
  the keepout has no trough ceiling solid yet (U1 depth measurement).
- Main-board envelope: not in the keepout set (photo-ESTIMATED only).
- FFC egress: OPi's 24pin FFC position is U15/U18.
- The battery-bay keepout is a coarse 60×34 box; the real bay walls
  are curved.

## Next

1. Add the main-board envelope solid from the photo analysis (with
   explicit ESTIMATED class) and re-run the check for the overhang.
2. Add the trough ceiling after U1 (ruler-into-cavity photo).
3. Then declare OP-B confirmed/rejected and fix the PCB outline rule.
