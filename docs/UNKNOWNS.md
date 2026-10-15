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
- PHOTO UPDATE (2026-10-15, drop 3): the 20 mm ruler read went through
  the UMD drive wiring hole on the joystick-side face — it is a chord
  read, NOT a door-side cavity depth.  **The scan values remain
  authoritative for cavity geometry** (main opening 47×50, rim z 8.7,
  floor z 1.3-3.1, trough channel y 58-70).
- CUT AUTHORIZATION (user, 2026-10-15): cutting plastic to enlarge
  the space is acceptable — so the usable volume is defined by the
  cut study (remove UMD-only bracket/ribs/trough interior; preserve
  bosses, hinge/latch, perimeter, battery structure), not by the
  as-scanned cavity.
- Blocked: cut-study execution (FreeCAD) is now the path; ruler face
  for the 40 mm tape read still pending.
- Status: SCAN-AUTHORITATIVE + cut study authorized.

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

## U9: J1 (Amphenol F32Q-31P) 3D model availability
- What: No vendor STEP model ships with KiCad 10 for the Amphenol F32Q
  0.5 mm 31-pin FPC connector (only Hirose FH12 30S/32S and FH26 31S/0.6 mm
  exist in the standard 3D library).
- Why it matters: STEP export of the SVDI breakout board currently contains
  the board outline and J2 only; J1 is missing from the mechanical check.
- How to resolve: download the Amphenol F32Q STEP from amphenol-icc.com
  (drawing f32q-f32t.pdf links the 3D model), place it under
  pcb/svdi-breakout/3dmodels/, and reference it with an absolute-ish path
  or ${KIPRJMOD}.
- Blocked: mechanical interference check of the breakout board (low risk:
  the board is a bench tool, not shell-mounted).
- Status: OPEN (documented gap; does not gate the capture-board design).

## U10: TPS62130 3D model missing (VQFN-16 3x3 EP1.45)

- What: KiCad 10's Package_DFN_QFN.3dshapes has no STEP for
  VQFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm (only Texas_RSA VQFN-16 4x4).
- Why it matters: exports/power-board.step is missing U3, so mechanical
  interference checks of the power board would silently exclude the
  buck converter.
- How to resolve: download the TI/Texas Instruments VQFN-16 (RGT)
  STEP from ti.com's product folder or a paid CAD-model service, place
  it under pcb/power-board/3dmodels/, and update U3's footprint 3D
  field.  Alternatively switch the footprint to the 4x4 Texas_RSA
  variant only if the datasheet confirms an RSA-package part number
  (TPS62130RSA is a different package - verify before substituting).
- Blocked: mechanical interference check of the power board (the board
  is also still unrouted and an ESTIMATED 105x45 exploratory envelope,
  so interference is not meaningful yet anyway).
- Status: OPEN (does not gate the schematic, which is ERC-clean).

## U11: STAT level shift for the Radxa GPIO (3.3 V max vs REGN 4.7 V)

- What: the BQ25895 STAT open-drain output is currently pulled up to
  REGN (4.7 V) by R8 on the power board, but the harness target is a
  Radxa ZERO 3W GPIO whose absolute maximum is 3.63 V.
- Why it matters: connecting J3.9 to the Radxa without changing the
  pull-up rail would over-stress the SoC pin.
- How to resolve: make STAT an open-drain net pulled up on the Radxa
  side (3.3 V through the GPIO's internal/external pull-up) and remove
  R8's REGN pull-up on the power board.  One schematic edit plus
  re-route; scheduled for the next power-board schematic revision.
- Blocked: nothing (design change, no measurement needed).
- Status: RESOLVED-IN-DESIGN (v1 board retired; v2 supervisor STAT
  line is pulled to its own 3.3 V domain — see system-architecture §5).

## U12: Front-shell display aperture depth (NEW, v2)

- What: z-space available behind the display window (front glass inner
  face → first obstruction) across the active area; plus bezel-lip
  width around the window.
- Precision: 0.1 mm.
- Why: replacement panel modules are 3.0–4.5 mm thick (stock glass was
  2.2 mm); the module + bridge-PCB stack must fit.  This single number
  decides the panel candidate (display-candidates.md #1 vs #3) and
  whether the bridge sits directly behind the module.
- How: donor shell, depth gauge through the window at ≥5 points.
- PHOTO UPDATE (2026-10-15, drop 2): a clear reproduction FRONT SHELL
  (skeleton, new-in-bag) is in hand — ribs/bosses visible through the
  plastic, display window + blue center ring (~Ø50 mm).  A straight-on
  window close-up with the ruler across the window edge can now answer
  the bezel-width half of this unknown without disassembly.
- Blocked: panel order, bridge board outline, display stack freeze.
- Status: OPEN — top v2 mechanical blocker (skeleton shell enables
  the measurement).

## U13: Bezel lip width and window border (NEW, v2)

- What: window border band width (shell side) around the active-area
  window; whether a cover-glass-extension panel can hide glass-vs-
  window mismatch (101.5–105.5 mm candidate glass vs 103.6 mm stock).
- Precision: 0.2 mm.
- Why: candidate outlines differ by up to 4 mm; the visible result
  must stay stock-looking.
- How: donor shell, calipers on the window edge.
- Blocked: panel candidate final selection.
- Status: OPEN.

## U14: Button FPC pinout, matrix map, stick reference rail (NEW, v2)

- What: FPC pin count/pitch; row/col matrix membership of every
  button; pull-up/down locations; analog stick pot ends/wiper and its
  reference rail's source (PSP MB rail vs battery).
- Precision: electrical map exact (continuity); resistances to 1%.
- Why: the v2 input interposer's sense taps and MCU-side scan-drive
  FETs depend on it; wrong assumptions here break both ARK pass-
  through and OPi-only input.
- How: donor unit + multimeter continuity map; scope the scan while
  pressing buttons (the stock MB scans continuously).
- Blocked: input interposer schematic (input-architecture.md §5).
- Status: OPEN.

## U15: Orange Pi Zero 2W as-measured geometry (NEW, v2)

- What: hole positions (hole Ø 3.0 mm is VERIFIED, positions are not),
  max component height over the board, bottom-side protrusion, exact
  24pin FPC exit position.
- Precision: 0.1 mm.
- Why: mechanical-layout.md OP-B placement and any OPi standoffs.
  Current 3.5 mm-inset hole positions are ESTIMATED from the
  Raspberry Pi Zero mechanical family — not verified for the OPi.
- How: calipers on the donor OPi board when purchased.
- Blocked: OPi mounting features on v2 boards, co-stack simulation.
- Status: OPEN.

## U16: Stock PSP motherboard current profile (NEW, v2)

- What: PSP-3000 MB supply current in menu/gameplay/sleep (stock
  battery terminal), to replace the ESTIMATED 1.2 A ceiling in
  power-budget.md.
- How: donor console, USB power meter inline on a bench supply at the
  battery terminal voltage.
- Why: ARK-mode endurance arithmetic and the v2 SYS rail sizing.
- Blocked: final power-budget freeze (architecture-level numbers are
  already conservative).
- Status: OPEN.

## U17: Battery pack ID/thermistor behavior (NEW, v2)

- What: stock pack terminal count and behavior (ID resistor? NTC?
  open?), pack connector family (do not assume JST-PH).
- PHOTO UPDATE (2026-10-15, docs/photo-analysis-donor-shell.md): the
  pack connects through a small PCB with a gold-plated contact row at
  the bay's upper edge — a contact-plate interface, not a wire
  harness.  The v2 pack path must reproduce the contact-plate
  geometry; exact contact count/pitch still needs the close-up.
- Why: the v2 pack path feeds the stock MB in ARK mode; the MB may
  refuse to boot or mis-charge with wrong ID lines.  Safety-relevant.
- How: donor pack + multimeter; contact-row close-up photo.
- Blocked: v2 battery-path schematic detail (power section).
- Status: OPEN (interface family narrowed: contact plate).

## U18: OPi Zero 2W 24pin FFC pin-level pinout (NEW, v2)

- What: pin-by-pin function of the 24pin expansion FFC (the manual
  lists capabilities: USB2.0 ×2, 100M eth, analog audio, TV-OUT,
  power button, 2× LRADC — the per-pin map exists only as images in
  `cad/references/orangepi-zero2w/opi24pin*.png`, which the tooling
  could not read reliably).
- Why: the v2 harness from OPi to power/supervisor boards uses this
  FFC; wrong pin map = dead board.
- How: (a) read the wiki images with reliable tooling; (b) confirm
  against the donor board with a multimeter once U15 happens.
- Blocked: harness connector selection + OPi-side schematic.
- Status: OPEN.
