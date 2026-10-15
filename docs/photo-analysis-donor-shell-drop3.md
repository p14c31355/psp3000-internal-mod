# Donor shell photo analysis — drop 3 (2026-10-15 evening depth shots)

Two measurement shots (16:41, 16:42 JST).  Vision reads succeeded on
the 400px thumbnails; zoom reads hit tool timeouts, so the fine
detail comes from user confirmation.

## Shot 164142_13730 (16:41) — tape measure into the cavity — CONFIRMED

**User confirmation (2026-10-15):** the tape's **zero rests on the
cavity floor of the removed UMD drive site**.  So the 40 mm reading
is a straight-line span from the cavity floor along the opening axis
to where the tape bends at the opening edge.

- Readable graduations: 10 / 20 / 30 / 40 (50 red).
- Cross-check with the scan: the main opening Y span is 50 mm (y
  14..64); a 40 mm straight-line insert from the floor to the edge is
  consistent with the opening's chord geometry (the tape does not
  follow the curved walls).
- **Donor-measured value:** cavity floor → opening edge ≈ **40 mm**
  along the insert axis.  This corroborates the scan's opening scale
  (50 mm Y span) with a real physical read and confirms the cavity
  floor is reachable/open at that axis — the UMD-mechanism structure
  (spindle mount, laser sled rails) is indeed gone or already below
  the insert path.

## Shot 164249_13731 (16:42) — steel ruler through the wiring hole

**User correction (2026-10-15, supersedes the earlier CONFIRMED
reading):** the ruler was inserted through the **UMD drive wiring
hole on the joystick-side face**, zero on the lid's inner face.
Therefore:

- The 20 mm span is **not** a door-side cavity depth.  It is a read
  along the wiring-hole axis (a chord through the structure between
  the joystick-side face and the cavity interior/bottom).
- **The scan values (REFERENCE_SCAN) remain the authoritative cavity
  geometry**: main opening 47×50 mm, rim z 8.7, visible floor z
  1.3-3.1, door trough channel y 58-70.
- The 20 mm read is still useful as a secondary check: it confirms a
  ~20 mm clear span exists along that hole axis, i.e. the interior
  structure in that direction is no shallower than the scan implies.

## Cut study — user authorization note

User states cutting plastic to enlarge the space is acceptable (the
owner already authorized cutting UMD-mechanism-only internal plastic;
this re-affirms it).  Consequence: the usable cavity is NOT the
as-scanned cavity — the cut study defines it by removing:

- the drive-mount bracket (if confirmed UMD-only),
- UMD-only support ribs inside the cavity walls,
- the door-trough interior structure that existed for the drive,
  while preserving: perimeter, screw bosses, hinge/latch structure,
  speaker mounts, structural ribs, battery structure.

The scan's obstruction map (bosses >16 mm, rib grid) is the keepout
list for that cut.

## Measurement status

- **13730 (40 mm): CONFIRMED** — tape zero on the removed-drive cavity
  floor; 40 mm straight-line span to the opening edge.  Corroborates
  the scan's 50 mm Y-opening chord geometry.  Recorded in U2.
- **13731 (20 mm): re-interpreted** — wiring-hole chord read, not a
  cavity depth.  Scan remains authoritative for cavity geometry.
