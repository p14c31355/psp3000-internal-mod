# PSP-3000 mechanical parameters (single source of truth for CAD)

Conventions:
- Units: millimeters.
- Coordinate system: X right, Y up, origin at bottom-left corner of the
  front face (LCD side), Z toward viewer (out of the screen). Body outline
  = the outer silhouette projected on XY.
- Every value carries provenance class:
  VERIFIED_FROM_PRIMARY_SOURCE (VPS) / VERIFIED_FROM_RELIABLE_SOURCE (VRS)
  / MEASURED / DERIVED / ESTIMATED / UNKNOWN.
- This file is consumed by cad/psp3000_model.py. Values marked ESTIMATED
  or UNKNOWN are rendered as explicitly flagged geometry or left hollow;
  they never silently become manufacturing constraints.

## Body envelope

param | value | class | source
---|---|---|---
BODY_W | 169.4 | VPS | Sony/SCEE PSP-3000 official product overview (WxDxH 169.4x18.6x71.4)
BODY_D | 71.4 | VPS | same
BODY_H | 18.6 | VPS | same (excludes largest projection)
BODY_CORNER_R | 6.0 | ESTIMATED | rounded-corner radius, visual estimate; refine from donor photos
SHELL_T | UNKNOWN | UNKNOWN | wall thickness, needs donor measurement (U1)

## LCD module (panel only; face glass/bezel separate)

param | value | class | source
---|---|---|---
LCD_W | 103.6 | VPS | Sharp LCM-09006 Table 5
LCD_H | 64.35 | VPS | same
LCD_T | 2.2 | VPS | same
LCD_ACTIVE_W | 95.04 | VPS | same
LCD_ACTIVE_H | 53.856 | VPS | same
LCD_X | UNKNOWN | UNKNOWN | X position of panel center; needs donor measurement (U1/m1.6)
LCD_Y | UNKNOWN | UNKNOWN | Y position of panel center; same
LCD_FPC_EXIT | UNKNOWN | UNKNOWN | which edge + position the 31-pin FPC exits; donor photo (m1.6)

## Battery

param | value | class | source
---|---|---|---
BAT_W | 58.7 | VRS | vendor listing PSP-S110 (2.31 in)
BAT_D | 36.0 | VRS | vendor listing (1.42 in)
BAT_T | 10.2 | VRS | vendor listing (0.4 in)
BAT_POS | UNKNOWN | UNKNOWN | battery pocket position; donor (m1.5)

## UMD cavity

param | value | class | source
---|---|---|---
UMD_CAVITY | UNKNOWN | UNKNOWN | full extent after drive removal (U2); donor measurement campaign 1
UMD_DOOR_CLEAR | UNKNOWN | UNKNOWN | min clearance to closed door (U2)

## Screw bosses

param | value | class | source
---|---|---|---
BOSS_XY | UNKNOWN | UNKNOWN | list of standoff XY positions (U3); donor
BOSS_DIA | UNKNOWN | UNKNOWN | standoff bore diameter

## Candidate SBC (Radxa ZERO 3W)

param | value | class | source
---|---|---|---
SBC_W | 65.0 | VRS | Radxa docs / vendor pages (65x30)
SBC_D | 30.0 | VRS | same
SBC_H_MAX | UNKNOWN | UNKNOWN | max component height incl. connectors on top; needs board photos + datasheet (open)
SBC_HOLE_PITCH | UNKNOWN | UNKNOWN | mounting hole positions; needs mechanical drawing (open)
