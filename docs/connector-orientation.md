# Connector orientation rules — v2 (mandatory)

Updated: 2026-10-15.  Status: rules frozen; per-connector table fills
in as schematics land.  Background: the v1 board's J1/J3 placements
were moved by DRC clearance instead of mechanical truth, and cable
side was never recorded — this document exists so that cannot recur.

## 1. The 7-point checklist (every connector, no exceptions)

For each connector in the design, record ALL of:

1. Datasheet pin numbering (with the datasheet figure number).
2. Footprint pin numbering as KiCad will place it.
3. Mating connector orientation (which side of the mate is pin 1).
4. PCB side: connector body on top or bottom of its board.
5. Cable contact side: for FFC, contacts up or down in the connector.
6. Assembled orientation: where this connector points in the closed
   PSP (direction + neighbor obstruction).
7. 3D render inspection with the mating cable drawn.

An entry is not complete until all 7 have values.  A schematic that
passes ERC with an orientation error is still WRONG.

## 2. FFC/FPC rules (0.5 mm pitch, the project standard)

- "Top-contact" connector = contacts touch the cable's **top**
  (insulator-up) face when the cable slides in with conductors DOWN.
  Bottom-contact = mirror.
- Cable enters the connector opposite its contact face: top-contact
  connector ⇒ conductors face DOWN toward the connector floor.
- Pin 1 convention: recorded per connector from its datasheet drawing
  (not assumed from KiCad), and the interposer/bridge PCB mirrors the
  cable's conductor side, never guesses it.
- Bend radius: conductors on the outside of a bend must face AWAY
  from the bend center... recorded per route in the mechanical model
  (docs/mechanical-layout.md §6, min 3 mm radius for 0.5 mm FFC).

## 3. Board-to-board FFC (v2 partitions)

| Link | From | To | Pins | Speed class | Contact side (cable) | Pin 1 | Assembled direction |
|---|---|---|---|---|---|---|---|
| L1 | power board | display bridge | 8 | I2C + rails | TBD at schematic | TBD | TBD (finalized with mechanical-layout.md) |
| L2 | power board | supervisor/input | 10 | UART + rails + strap | TBD | TBD | TBD |

No high-speed nets cross a board boundary (system-architecture §7).
HDMI lives and dies on the bridge board.

## 4. Panel FFC (the critical one)

Panel-side FFC from the ST7262E43-class module: 40-pin 0.5 mm.
Conductor side and pin-1 corner are recorded per candidate in
`docs/display-candidates.md` at schematic time — the CDTech drawing
shows pin 1 = LED-A(1) at the corner; VERIFY against the ordered
part's drawing before the bridge schematic (the Maclight-class
alternates exist).

## 5. Wire/other connectors

| Connector | Function | Checklist status |
|---|---|---|
| USB-C (charge) | power in | re-verify against shell cutout position at placement time — v1 failure mode |
| JST-class battery | pack + thermistor | pack connector type UNKNOWN (U17 covers ID; connector family measured with donor pack — do not assume PH) |

## 6. Process rule

Placement step of any PCB in v2 is not "done" until §1 rows exist for
every connector on that board AND the 3D render with cables passes
eyeball inspection by the reviewer (the user, for final; the agent,
for intermediates).
