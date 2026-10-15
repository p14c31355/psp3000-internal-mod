# Donor shell photo analysis — drop 3 (2026-10-15 evening depth shots)

Two measurement shots (16:41, 16:42 JST).  Vision reads succeeded on
the 400px thumbnails; zoom reads hit tool timeouts, so the fine
detail (which face the tape zero rests on) is pending user
confirmation.

## Shot 164142_13730 (16:41) — tape measure into the cavity

- Stainless tape (No. 13005), 0 end hidden inside the opening, the
  tape bends at the opening edge over the **"40" graduation**.
- Readable graduations: 10 / 20 / 30 / 40 (50 red).
- Shell stood on edge; the tape runs along the opening axis.
- **Interpretation (to confirm):** the cavity's long-axis (Y)
  dimension ≈ 40 mm of insertable depth before the bend — but the
  tape could also be following a curved wall, and standing the shell
  suggests the tape may be reading along the body's short axis.
  REFERENCE_SCAN cross-check: the cavity main opening Y span is
  50 mm (y 14..64), so a 40 mm readable insert is plausible for a
  straight-line partial depth, not the full opening.

## Shot 164249_13731 (16:42) — steel ruler into a recess — CONFIRMED

**User confirmation (2026-10-15):** the ruler's **zero rests on the
inside (back) of the UMD lid**.  So the ~20 mm reading is the distance
from the UMD lid's inner face to the measured face.

- Cross-check with the scan: the UMD lid itself is a ~1.4-2 mm thin
  shell; the lid's inner face sits just below the rim band (rim z
  7.7-9.9 in body coords).  A 20 mm span from the lid's inner face
  reaches well past the cavity floor level (floor visible at z
  1.27-3.08) — consistent with the ruler crossing the cavity and
  landing on the structure at its bottom (disc-well floor / bracket).
- **Working value (donor-measured, pending one more read):** UMD lid
  inner face → cavity bottom structure ≈ **20 mm**.  This bounds the
  cavity's z depth from the door side: door-side available stack depth
  ≈ 20 mm minus the lid thickness — far more than the 7-8 mm that the
  battery-side rim band suggested, which means the cavity is deeper
  than the battery-side rim implies and the door-trough side is the
  generous direction.

## Consequence for OP-B (upgrade in confidence)

The OP-B split-z placement's binding constraint was the rim height
(0.98 mm headroom at the battery side).  With a ~20 mm door-side
depth, the second level (over the trough, under the lid) has real
room: lid inner face minus ~1.4-2 mm lid + 20 mm span reaches the
bottom structure; a board + components (1.2 + 5.0 = 6.2 mm) fits
under the lid with large margin.  The cut study must now verify what
structure the ruler landed on at the 20 mm face (if it is the drive
mount bracket, that bracket is UMD-mechanism-only and may be cut).

## What this pair would establish once confirmed

If 13731's 20 mm is "table zero → recess opening plane", it is a
z-thickness read (matches 13724's method result).  If it is "recess
floor → recess rim", we have the first true U1-style interior depth
number, and the recess identity (UMD cavity vs battery bay vs MB
pocket) decides where it lands in the UNKNOWNS register.

## User confirmation status

- **13731 (20 mm): CONFIRMED** — ruler zero = UMD lid's inner face.
  Donor-measured span lid-inner-face → bottom structure ≈ 20 mm.
- **13730 (40 mm): still pending** — which face the tape zero rests
  on.  Once confirmed it lands in U2 (cavity long-axis) or U1.
