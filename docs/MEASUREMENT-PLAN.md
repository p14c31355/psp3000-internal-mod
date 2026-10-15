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

## Campaign 3 — SVDI capture (DEPRIORITIZED in v2)

The v2 architecture replaces the stock panel with a generic RGB panel
(system-architecture §2), so the SVDI symbol-packing reverse-engineering
(U6) is no longer on the critical path.  It is retained only as the
fallback if the ARK USB-streaming path fails bring-up.  Existing SVDI
breakout hardware remains usable for that contingency.

## Campaign 4 — v2 donor measurements (unlocks v2 PCB outlines)

| ID | Measurement | Where | Unlocks |
|---|---|---|---|
| m4.1 | Display aperture depth + bezel lip (U12/U13) | donor front shell, depth gauge through the window, ≥5 points | panel order + bridge outline |
| m4.2 | Button FPC pinout + matrix map + stick rail (U14) | donor, multimeter + scope on the live scan | input interposer schematic |
| m4.3 | UMD cavity walls/depth + trough relief (U1/U2 v2 extent) | donor, drive removed | OPi OP-B placement freeze |
| m4.4 | OPi Zero 2W hole positions + component heights (U15) | donor OPi board, calipers | OPi mounting features |
| m4.5 | OPi 24pin FFC pin map (U18) | wiki images; confirm on donor | harness connector |
| m4.6 | Stock MB current profile (U16) | donor console + bench supply | power-budget freeze |
| m4.7 | Pack ID/thermistor + connector family (U17) | donor pack + shell | battery-path schematic |

Priority order: m4.1 → m4.3 → m4.2 → m4.4/m4.5 → m4.6/m4.7.

## Standing rule

A measurement without a recorded source, tool, and tolerance is not a
measurement. Do not proceed to dependent design steps from unrecorded data.
