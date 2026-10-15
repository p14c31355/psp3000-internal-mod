# Mechanical layout v2 — UMD-cavity partitioning

Updated: 2026-10-15.  Status: DRAFT — numeric anchors are classified
per AGENTS.md; PCB outlines may not be drawn from this document until
the U1/U12/U13 donor measurements land.

## 1. Fixed mechanical truth (carried from cad/params.md + verified sources)

| Item | Value | Class |
|---|---|---|
| Body | 169.4 × 71.4 × 18.6 mm | VPS (Sony spec) |
| LCD module stock | 103.6 × 64.35 × 2.2 mm | VPS (Sharp) |
| UMD disk | Ø60 mm | VPS |
| Battery bay | PSP-110 battery (44.4 × 33.7 × 8.2 mm) region, right rear | VPS (battery label); exact bay border UNKNOWN |
| Main board volume | left/rear region under D-pad side | ESTIMATED (iFixit photos, no scale) |
| Speaker volumes | both ends of the top face | ESTIMATED |

## 2. Available volume after UMD removal

The UMD drive occupies the right ~55 mm of the body between the shell
walls, roughly z = 2..10 mm above the back shell floor at the disc
well, wider below the door trough.  After cutting UMD-only support
plastic (permitted list), the usable envelope is approximately:

- Disc well: Ø60 mm cylinder, ~10-12 mm deep (ESTIMATED — U1/U2
  donor measurement required for depth and exact wall position).
- Under-door trough: ~64 × 14 mm strip along the door, shallow
  (ESTIMATED — U1).
- The cavity is open toward the main-board side after the drive's
  right-angle connector area is cleared.

Nothing here is yet a board outline.  The Ø60 inscribed-rectangle
48×36 mm from the v1 analysis is retained only as a sizing aid — the
v2 rule is that outlines come from wall-to-wall measurements of the
real cavity (U1/U2), not from inscribed rectangles.

## 3. Component anchors (mechanical, from system-architecture §7)

| Anchor | Why fixed | Volume needed |
|---|---|---|
| Battery + BQ25895 power section | battery bay is fixed by the shell; charger must sit at the pack terminal | ~45 × 20 mm strip adjacent to battery bay (ESTIMATED border) |
| Supervisor/input board | at the button-FPC egress under the left controls | ~25 × 15 mm (interposer + MCU) |
| Display bridge board | at the new panel's FPC, behind the glass, z-stacked behind module | ≤ panel glass width; ~55 × 25 mm if at the panel's lower edge |
| OPi Zero 2W | 65 × 30 flat plate + components ≤ 4.5 mm top / ~2 mm bottom | needs 65 × 30 planar area, cable egress on one short edge |
| Speakers | existing mounts — untouched | stock |

## 4. OPi Zero 2W placement study (to be simulated, not yet run)

Candidate placements for the 65 × 30 board:

- **OP-A: disc well, horizontal, face-down** — 65 mm does not fit the
  Ø60 cylinder chord-by-chord (max chord at 30 mm offset = 2·√(30²−15²)
  = 51.96 mm < 65) → **geometrically impossible flat**.  Only diagonal
  with overhang into the trough — reject unless the well depth
  (U1/U2) proves generous.
- **OP-B: split-z stack in the well + trough** — OPi bottom half in
  the well floor, top half over the trough at higher z; requires the
  trough to be free of the door mechanism at that z (door trough is
  exterior; interior side is free after drive removal).  Feasible on
  paper; needs U1/U2 depth numbers.
- **OP-C: main-board-side volume** — replacing the stock main board
  region: OPi sits where the stock MB was, 65×30 fits the left
  region, but then the stock MB must shrink/move → conflicts with
  ARK mode (stock MB must remain functional).  Reject: ARK mode
  requires the stock MB in place.
- **OP-D: above the main board (stacked)** — z = 10..15 mm band above
  the stock MB on the left side; the body is 18.6 mm total, LCD
  module + front shell consume z ≈ 8..18.6 at the front → remaining
  gap above the MB is ~4-6 mm — insufficient for OPi's component
  height.  Reject by z-stack arithmetic unless front glass area is
  included (it is not — display occupies it).

**Provisional selection: OP-B**, pending U1/U2 cavity measurements.
OP-A is arithmetically excluded (51.96 < 65 chord — recorded so nobody
re-derives it).  The OPi's 24pin FFC egress must face the
main-board/bridge side; 40pin header is not populated (fine — we use
the FFC + USB).

## 5. Display assembly stack (behind the front shell)

Front shell → glass/aperture (U13 bezel) → panel module (3.0-4.5 mm,
U12 decides which candidate) → bridge PCB (≤1.6 mm, 4-layer) directly
behind the module with the 40-pin FFC on its top face → panel FPC
folds over the bridge edge.  Total behind-glass stack ≈ module + 2.5
mm.  Stock allowed ≈ 2.2 + T-CON cavity (unknown, U12).  **This stack
arithmetic is the single biggest mechanical risk of v2** — it decides
between candidates 1 (4.53 mm) and 3 (~3.0 mm) or forces a cover-glass
redesign.  Measurement U12 is the unblock.

## 6. FreeCAD simulation plan (after donor numbers)

1. `cad/psp3000_model.py` cavity solids updated with U1/U2 measured
   walls (replace ESTIMATED faces).
2. OPi STEP: build from verified 65×30×1.2 + component-height envelope
   (parts ≤4.5 mm over the 30 mm span — from board photos; class
   VRS until the donor board is calipered).
3. Bridge + panel module solids per selected candidate datasheet
   (VERIFIED dimensions from its drawing).
4. Interference check of: OP-B stack, panel stack, battery clearance,
   speaker clearance, screw bosses, door hinge sweep.
5. FFC bend radius: 0.5 mm-pitch FFC minimum bend ≈ 3 mm radius —
   routed in the model as arcs, not straight lines.

## 7. Measurement requests (blocks PCB outlines, not architecture)

- U1: UMD cavity walls/depth (shell interior, after-drive volume).
- U2: trough depth + door interior relief.
- U12: aperture depth behind glass (module + bridge z budget).
- U13: bezel lip width.
- U14: button FPC pinout + matrix map + pull locations.
- U15: OPi Zero 2W hole positions + component max height (donor
  board, calipers).
