# Power board DRC exception record (Phase 6, rev A routing)

Date: 2026-10-13.  Board: `pcb/power-board/power-board.kicad_pcb`.

## State (placement revision 4 - 48x36 measured-envelope fit, 2026-10-13)

- ERC (schematic): **0 violations** (`kicad-cli sch erc --severity-all`).
- DRC (board): **7 clearance violations**, all via-to-track
  (0.08-0.12 mm measured vs 0.10 required), plus 3 GND-zone island
  ratsnest reports.  0 unrouted nets; no courtyard overlaps, no
  shorts.
- Zone-island reports: the F.Cu ground pour fragments into 7 islands
  around the dense passives; 13 stitching vias already tie most of
  them to the B.Cu plane, but 3 island-pairs still report unconnected
  because every clear spot tried so far either collides with a track
  (0.08-0.12 mm) or sits inside a fill cut-out.  Adding more vias
  fragments the pour further (verified: attempts increased the count).
- Board outline: 48 x 36 mm - the largest rectangle inside the
  DERIVED 60 mm UMD disc cavity (`cad/power_board_sizing_probe.py`).
  All 21 footprints verified inside the outline (pad-extent check).
- Root cause: freerouting 1.6.2 lays out with the 0.4 mm via padstack
  and then the vias are widened to 0.5 mm, eating the margin.
  Relocating vias by hand was tried interactively across several
  sessions; each relocation traded a clearance violation for a
  shorting/dangling violation.  The freerouting geometry is locally
  optimal under its own assumptions.
- Additional change: R8 (STAT pull-up to REGN) removed - STAT is
  open-drain, pull-up moves to the Radxa side at 3.3 V (U11,
  `docs/harness-j3-radxa.md`).

## The two accepted exceptions

Both are via-to-track spacing created by freerouting 1.6.2's routing:

1. `/SDA` via @(26.63, 20.05) vs `/SCL` F.Cu track — measured
   clearance 0.0801 mm vs 0.10 mm required.
2. `/STAT` via @(27.94, 14.87) vs `/REGN` F.Cu track — measured
   clearance 0.1060 mm vs 0.10 mm required (this one actually passes
   at 0.10; it is listed because the netclass default of 0.13 flags
   it under stricter settings).

## Why accepted (and what would fix them properly)

- freerouting 1.6.2 computes via clearances against the DSN padstack
  *name* (400:200 um) even when the padstack *shape* is patched to
  500:300 um; widening the vias afterwards therefore eats into the
  track clearance.  Re-routing with a correctly-specified larger via
  (or a newer freerouting that honours the patched shape) would remove
  both.
- Moving either via by hand breaks its connected track geometry
  (verified interactively; each attempted relocation traded a
  clearance violation for a shorting or dangling violation).
- The board is still an ESTIMATED exploratory envelope (105 x 45 mm,
  U1-U5 donor measurements pending).  Before any fabrication order,
  the placement will change to the measured envelope and this routing
  will be redone anyway, which supersedes these exceptions.

## Conditions for review

- Re-evaluate on the next placement revision (mechanical envelope from
  donor measurements).
- Do not order fabrication of this revision without re-running the
  freerouting pass with the via padstack fixed at the source.
