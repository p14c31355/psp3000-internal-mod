# Failure analysis of the 48×36 mm power-board prototype (rev 4)

Date: 2026-10-14.  Verdict: **reference only; do not repair or re-route.**
Branch: the board lives at `pcb/power-board/` on main (merged PR #2).
A replacement architecture starts at `docs/system-architecture-v2.md`.

## 1. Why its PCB area is poorly utilized

Measured on `pcb/power-board/power-board.kicad_pcb` (placement rev 4):

| Metric | Value | Consequence |
|---|---|---|
| Board area | 1 728 mm² (48×36) | fixed before placement, not after |
| Sum of pad copper | ~155 mm² (~9 %) | the board is mostly empty copper |
| Sum of footprint bboxes | 3 056 mm² | includes silkscreen text scatter |
| Total routed length | 491 mm | unusually long for 21 parts — parts sit far apart |
| Largest single consumer | J1 USB-C body spanning 48 mm | connector, not circuit, dictates the outline |

Diagnosis: the 48×36 outline came from a **desk exercise** ("largest
rectangle inside the derived 60 mm UMD disc circle"), not from the
physical location of that circle inside the PSP.  The UMD cavity is not
a free 60 mm disc — it is a specific pocket bounded by the shell wall,
the battery bay and the mainboard.  A rectangle that fits the circle
mathematically can still fail the pocket, and does.

Functional grouping was also absent: R6/R7 (I2C pull-ups) sit on the
top strip 15 mm from U1 (the pins they serve), R10/R11 (TS divider)
sit even further away, C1 (PMID bypass) is 20 mm from U1 pin 23.
Datasheet-recommended tight loops (BQ25895 §10.1 layout: PMID/BAT caps
"close to IC") are not satisfiable at these distances.

## 2. Which connector orientations are suspect or unverified

| Connector | Status | What was verified | What was NOT |
|---|---|---|---|
| J1 USB-C (GCT USB4105) | footprint placed by coordinates | symbol pinout from KiCad lib | position/orientation vs the PSP bottom edge; which shell cutout it must align with |
| J2 JST-PH 2pin (battery) | placed ad hoc | nominal polarity | which side the stock battery lead exits the bay; whether a JST-PH even mates the stock S110 pigtail (it does not — stock is a different connector) |
| J3 2×05 header (to SBC) | rotated 90° during placement to make DRC pass | electrical pin map (`docs/harness-j3-radxa.md`) | whether a 2×05 header is physically reachable inside the shell after assembly, and whether the harness flex can route to the Radxa |
| (missing) PSP-button FPC | absent from the board entirely | — | the whole input path was never designed |
| (missing) LCD FPC | absent | — | display bridge was never on this board |

The J1 placement was moved three times (rev 1→4) purely to satisfy DRC,
ending at "top edge" — an arbitrary choice.  In the real device the
USB-C receptacle must land at the shell's existing bottom-edge cutout,
which was never measured.

## 3. Which dimensions were arbitrarily inherited

| Dimension | Origin | Valid? |
|---|---|---|
| 48×36 mm outline | largest rectangle in a derived 60 mm disc | geometrically true, mechanically unproven (cavity ≠ disc) |
| 105×45 first outline | earlier desk estimate | superseded, and itself arbitrary |
| Board origin (0,0) | KiCad default | no relation to PSP datum |
| J2 battery connector = JST-PH | generic part choice | stock PSP-S110 uses a different plug — needs donor verification |
| 2-layer stackup | cost | fine for low-speed, but the board also carries the buck converter; a 4-layer would halve the loop areas |
| Board plane at z=1.0 | co-stack probe Option C | consistent with the Radxa stack but never validated against real wall/boss positions |

## 4. Mechanical assumptions missing (all UNKNOWN in UNKNOWNS.md)

1. U1 — shell inner wall thickness and inner offsets around the whole
   perimeter.
2. U2 — actual UMD-cavity extent after drive removal (the drive is a
   bracketed assembly; removing it leaves bosses/ribbons, not a clean
   prism).
3. U3 — screw boss positions and bores in the UMD cavity region.
4. U5 — battery connector geometry and polarization.
5. (new) PSP button FPC connector positions and pitch on the mainboard
   side (never catalogued).
6. (new) the bottom-edge cutout geometry that the USB-C receptacle must
   align to.
7. (new) speaker enclosure volumes — anything placed in the cavity must
   not touch them.

## 5. Circuits that remain usable

- **BQ25895 charge/power-path topology** — the part choice is sound for
  USB-C 5 V in, 3.8-4.2 V battery, OTG 5 V out; the *pin map* and
  design constants (`docs/evidence/bq25895-pinmap.md`) are verified
  against the TI datasheet and survive.
- **DW01A + dual-FET protection chain** — verified topology (standard
  DW01A datasheet circuit); carries over.
- **TPS62130 3.3 V buck** — verified pinout from the KiCad library
  symbol; carries over as a circuit block, though its board may merge
  with another partition.
- **The U11 decision** (STAT pull-up on the SBC side, not REGN) — the
  reasoning and the harness doc survive regardless of board shape.
- **The J3-to-Radxa pin map** (`docs/harness-j3-radxa.md`) — logic-level
  decisions survive even though the physical header probably becomes an
  FFC.

## 6. Circuits/approaches to discard

- The 48×36 board outline, all placement, all routing (491 mm of
  tracks) — geometry is the failure.
- The **single-board-for-everything partition**: one board cannot sit
  in the battery bay AND reach the USB-C cutout AND serve the display
  bridge.  The mechanical study (system-architecture-v2) shows the
  natural partition is power/supervisor in the UMD cavity, display
  bridge behind the LCD, and both connected to the Radxa by FFC.
- The **2×05 pin header as the SBC interconnect** — a 0.5 mm-pitch FFC
  is flatter, cheaper in height, and matches the Orange Pi 24-pin/40-pin
  expansion philosophy.
- J2 = JST-PH as the battery connector assumption.
- The idea that the board plane sits at z=1.0 in the same XY zone as
  the battery: the battery bay is not the UMD cavity; co-locating them
  was an artifact of the oversized rectangle overlapping both regions.
