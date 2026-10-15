# Donor shell photo analysis — first photo drop (2026-10-15)

Photos: DOOGEE Note58 Pro, 4672x3504, taken 2026-10-13 20:56 (2 shots)
and 2026-10-15 13:50-13:51 (2 shots).  Scale reference: stainless ruler
(mm) included in-frame in all shots — positions readable to ~2-3 mm
under perspective.  All values below are PHOTO-ESTIMATED (class:
ESTIMATED; not manufacturing constraints).  Files live outside the
repo at `~/dev/p20-root/shots/`.

## Shot inventory

| File | View | What it shows |
|---|---|---|
| 131837_13704.jpg (10-13) | internal, board side | green MB, big SoC chip, round speaker left, EMI shields right (UMD area), ribbon cables, white inner frame with bosses/ribs |
| 131846_13703.jpg (10-13) | internal, other angle | same teardown, second angle |
| 135234_13722.jpg (10-15) | internal, board side + ruler | full board-side view; speaker left, MB center, shield + UMD opening right |
| 135241_13723.jpg (10-15) | internal, battery side + ruler | battery bay with pack removed, UMD cavity opening (drive already removed), left small PCB with gold contacts |

## Photo-estimated findings (ESTIMATED)

1. **UMD cavity opening (battery-side view, 135241):** rounded-corner
   near-square opening, ~50 mm across both ways on the ruler (≈55→105
   mm band), aspect ≈1:1 to 1.2:1.  Consistent with the Ø60 disc well
   constrained by a squarish drive cutout — the usable free volume is
   closer to a rounded square than a full circle.  Reinforcement ribs
   form a grid/radial pattern around it; screw bosses at corners and
   mid-edges; snap-fit lugs on the perimeter.  The opening sits
   slightly right of center, upper-middle in the battery-side view.
2. **UMD drive status:** already removed in the 10-15 shots — the
   cavity is open, and the green MB is visible through it at the
   bottom edge (board sits below/behind the cavity floor on that
   side).  A black block (spindle-motor mount or connector) and a
   metal bracket remain at the cavity floor.
3. **Battery bay (135241):** pack removed; bay spans roughly the
   15→75 mm ruler band ≈ 60 mm long opening in this projection —
   consistent with the PSP-S110 pack (44.4 × 33.7 mm) plus guides.
   Contacts are on a small green PCB with gold-plated contact row at
   the bay's upper edge — NOT a wire-harness JST; pack connects via
   contacts on that small board (U17 update below).
4. **Battery label:** SONY, Model PSPJ-30000 body label; pack is
   3.6 V DC class (S110 family).  Serial 515051507 visible on the
   body label.
5. **Speaker:** one round black speaker visible at the LEFT in the
   board-side view (the second speaker is on the opposite side, not
   clearly captured in these angles).  Speaker diameter reads roughly
   20+ mm on the ruler band but exact value needs a dedicated close-up.
6. **Screw bosses:** ~6 clearly visible in board-side view (top edge
   x2-3, right side, bottom x2), more around the cavity and bay.
   All cylindrical, shell-colored, with dark screw-hole centers.
7. **Board (board-side view):** teal-green MB with a large black SoC
   on a shield, occupies the left/center; EMI shield plates cover the
   right region (over the UMD-adjacent area); ribbon cables route
   along the top edge toward the display side; a small green FPC board
   (△○×□ buttons) sits at the right edge.
8. **Body length check:** ruler reads the body at ~170 mm ≈ the
   169.4 mm spec — the ruler reference is trustworthy to ~±2 mm
   through this projection.

## Impact on v2 documents

- **mechanical-layout OP-B (split-z in cavity)**: the cavity floor is
  NOT clear — MB visible through the opening and a bracket at the
  floor.  OP-B remains plausible only in the volume ABOVE the floor
  and BELOW the door trough; the depth question (U1/U2) is now sharper:
  measure from cavity floor to door-trough ceiling.
- **Battery connection (U17)**: pack connects through a small PCB with
  gold contacts at the bay's upper edge (not a JST wire harness) —
  the v2 pack path must reproduce contact geometry, not a connector
  family swap.  Measurement request updated.
- **Cavity shape (U2)**: rounded-square ~50 mm opening on the
  battery-side projection — the "inscribed circle" mental model
  overstates free width in one axis; next probe should use the
  measured rounded-square, not Ø60.

## Still needed (photo campaign continues)

- Display-window close-ups (front shell, bezel + aperture depth) — U12/U13.
- Button FPC / left controls region — U14.
- A straight-down shot of the empty UMD cavity with the ruler across
  BOTH axes (for the opening map), and one with a depth gauge or a
  toothpick+caliper for depth — U1/U2 numbers.
- Speaker close-up with ruler — U8.
- OPi Zero 2W photos when the board arrives — U15.
