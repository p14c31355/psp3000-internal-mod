# Donor measurement plan (PSP-3000)

Purpose: convert every UNKNOWN in docs/UNKNOWNS.md into a recorded
measurement with units, tolerance, and coordinate reference, stored under
docs/measurements/ as CSV or markdown with provenance.

## Campaign 1 — shell + volume (unlocks Phase 2)

Required tools: digital calipers (0.01 mm), depth gauge, ruler, camera.

| ID | Measurement | Where | Target precision |
|---|---|---|---|
| m1.1 | Overall W/D/H with calipers (3 axes, 3 spots each) | donor body | 0.1 mm |
| m1.2 | Internal height grid (U1): under-LCD region, mainboard region, battery region, UMD cavity | donor, lid open | 0.1 mm |
| m1.3 | UMD cavity bounding box + hinge swing envelope (U2) | donor, drive removed | 0.5 mm |
| m1.4 | Screw boss XY + thread (U3) | donor, mainboard removed | 0.2 mm |
| m1.5 | Battery pocket inner dims (U4) | donor | 0.2 mm |
| m1.6 | LCD module seat: opening size, frame lip, FPC exit slot | donor, screen out | 0.1 mm |
| m1.7 | Bottom edge jack cutout + DC-in opening | donor | 0.1 mm |

Recording format: one markdown file per session with a photo reference,
all numbers annotated `[mm]`, coordinate origin = bottom-left of the FRONT
face, X right, Y up, Z toward the viewer. Tolerance notes mandatory.

## Campaign 2 — electrical truth (unlocks Phase 5)

| ID | Measurement | Method |
|---|---|---|
| m2.1 | Battery connector pinout (U4) | multimeter continuity donor-battery<->board |
| m2.2 | Button matrix map (U5) | multimeter on membrane FPC |
| m2.3 | Analog stick pot values (U5) | ohmmeter at end stops + center |
| m2.4 | Speaker impedance (U8) | ohmmeter (DCR; nominal 8 ohm expected) |
| m2.5 | LCD FPC continuity sanity vs. spec pin map | multimeter panel connector -> FPC tail |

## Campaign 3 — SVDI capture (unlocks Phase 4, highest value)

Goal: recover the exact symbol packing on DATA1/DATA2 between start/end
codes while a donor console renders a KNOWN test pattern (solid colors,
vertical bars).

- Equipment: logic analyzer >= 200 MSa/s with 2 GB memory (Saleae Logic Pro
  class) or FPGA capture board; LCD FPC breakout (0.5 mm 31-pin FPC to
  header adapter, custom or bought).
- Method: capture CLK±, DATA1±, DATA2± for >= 1 frame; decode DDR symbols;
  correlate frames against the displayed pattern; publish the mapping table
  and raw captures in docs/references/svdi-capture/.
- Alternative: obtain LR388G1 (Samantha) functional specification.

## Standing rule

A measurement without a recorded source, tool, and tolerance is not a
measurement. Do not proceed to dependent design steps from unrecorded data.
