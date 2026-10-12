# Unknown dimensions register

Rule (AGENTS.md): an UNKNOWN is never silently replaced by a nominal value.
Each entry states what to measure, between which surfaces, with what
precision, and why it matters. Blocked work is listed per entry.

## U1: Shell internal height profile
- What: distance between inner floor (where the OEM motherboard sits) and
  the inner face of the front shell / LCD frame, at a 10 mm grid over the
  area x=[5..165], y=[5..66] (body coordinates, origin bottom-left of front
  face).
- Precision: 0.1 mm.
- Why: determines maximum component height per region; blocks placement of
  SBC, bridge board, battery.
- How: donor unit, depth micrometer through removed UMD opening + under-LCD
  region; or calipers at shell openings.
- Blocked: Phase 3 placement, Phase 6 outlines.
- Status: OPEN.

## U2: UMD cavity free volume after drive removal
- What: bounding box of the cavity plus obstruction map (screw bosses,
  ribs, lid hinge swing envelope), donor unit.
- Precision: 0.5 mm envelope; bosses to 0.2 mm.
- Why: candidate SBC home; UMD-door clearance drives max height there.
- How: calipers + hinge swing photos; 3D scan preferred if available.
- Blocked: SBC selection freeze, door-latch verification.
- Status: OPEN.

## U3: Screw boss positions (motherboard region)
- What: XY of standoffs that accept OEM screws on the rear shell floor,
  diameters, thread spec (likely Phillips M1.7/M2 class).
- Why: new mainboard must reuse OEM bosses; do not drill the shell.
- How: donor, calipers; cross-check iFixit TA-090 teardown photos.
- Blocked: Phase 6 board outline + mounting holes.
- Status: OPEN.

## U4: Battery pocket and connector
- What: pocket inner dimensions; connector housing part number and pinout
  (terminals: P+, P-, TH/ID, possibly NTC).
- Why: charging design and mechanical retention; safety-critical (M4).
- How: donor; continuity-map connector pins to battery terminals with a
  multimeter; measure pocket.
- Blocked: Phase 5 power architecture freeze.
- Status: OPEN.

## U5: Button membrane electrical map
- What: connector pin to button mapping; series resistance per contact;
  analog stick pot end-to-end resistance and wiper ranges.
- Why: control board scan matrix design.
- How: donor + multimeter; photograph membranes.
- Blocked: control schematic (Phase 5/6).
- Status: OPEN.

## U6: SVDI symbol packing
- What: bit-level mapping of RGB888+syncs onto DATA1/DATA2 pairs between
  start/end codes (codes themselves are documented: VF=FF000003h,
  HF=FF000005h, VE=FF00000Ah, HE=FF000009h).
- Why: FPGA bridge TX RTL correctness.
- How: (a) locate Samantha (LR388G1) functional datasheet via Sharp/Sony
  channels; or (b) donor console: probe LCD FPC with a fast logic analyzer /
  SerDes capture at 54 MHz DDR and correlate with a known test pattern.
- Blocked: Phase 4 final architecture decision (bridge vs. alternate panel),
  Phase 6 bridge schematic.
- Status: OPEN — highest-risk unknown of the project.

## U7: FCC internal photos (secondary corroboration)
- What: AK8PSP3001/-D/-E internal photo PDFs from fcc.gov (fccid.io is
  bot-walled; archive.org was temporarily offline during attempt).
- Why: corroborate U1-U3 without a donor.
- How: retry fcc.gov OET or archive.org later.
- Blocked: nothing (corroboration only).
- Status: OPEN.

## U8: Speaker driver impedance and placement
- What: speaker nominal impedance (expect 8 ohm, verify), cavity positions.
- Why: amp selection (Phase 5).
- How: donor, ohmmeter.
- Blocked: amp part choice only.
- Status: OPEN.
