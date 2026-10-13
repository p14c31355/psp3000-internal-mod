# Power board DRC exception record (Phase 6, rev A routing)

Date: 2026-10-13.  Board: `pcb/power-board/power-board.kicad_pcb`.

## State

- ERC (schematic): **0 violations** (`kicad-cli sch erc --severity-all`).
- DRC (board): **2 clearance violations** out of a fully routed board
  (0 unrouted, all pads connected).
- Netclass clearance was set to 0.10 mm (4 mil, standard fabrication
  capability) before measuring; both remaining violations are below
  even that.

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
