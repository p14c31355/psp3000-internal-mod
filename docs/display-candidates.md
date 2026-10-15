# Display candidates — 4.3" 800×480 RGB replacement panel

Updated: 2026-10-14.  Goal: replace the obsolete Sharp LQ043T3LX02
(SVDI/proprietary T-CON) with a generic purchasable 4.3" 800×480 RGB
panel that physically fits the PSP-3000 front shell.

## Hard constraints from the PSP-3000 (mechanical truth)

| Constraint | Value | Class | Source |
|---|---|---|---|
| Original LCD module outline | 103.6 × 64.35 × 2.2 mm | VPS | Sharp LCM-09006 Table 5 |
| Original active area | 95.04 × 53.856 mm | VPS | same |
| Front-shell display aperture | ≈ active area + bezel lip | UNKNOWN | donor measurement (U12) |
| Space behind glass (module + bridge) | UNKNOWN | UNKNOWN | donor (U1/U2) |

Key implication: the **active area should be ≈95.04 × 53.856 mm**
(otherwise the front shell's window either shows dead border or crops
the image).  Panels whose active area matches 95.04×53.856 exactly are
the 4.3" 800×480 class — this is the same glass format family the PSP
used.

## Candidate table

| # | Part | Driver IC | Interface | Active area | Outline | Thickness | FPC | Brightness | Availability | Est. price | Fit risk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CDTech S043BWV106EP | ST7262E43-G4 | 24-bit RGB | 95.04×53.86 | 101.5×64.0×4.53 | 4.53 (with frame) | 40-pin 0.5 mm | 800 nit | vendor (China), datasheet public | ~$12-18 (TBD) | outline 101.5×64 < 103.6×64.35 ✓; thickness 4.53 exceeds stock 2.2 — needs shell-back clearance check |
| 2 | Maclight MLT043W40-12 | ST7262E43 | RGB 24-bit | 95.04×53.86 | 105.5×67.2×3.0 | 3.0 | 40-pin (pinout listed) | 800-900 nit | small-MOQ vendor | ~$10-15 (TBD) | outline 105.5×67.2 > 103.6×64.35 ✗ — glass wider than stock; needs bezel check |
| 3 | Generic ST7262E43 4.3" 800×480 (LCSC/AliExpress class) | ST7262E43 | RGB | 95.04×53.86 | typically 105.5×67.2×3.0 | ~3.0 | 40-pin 0.5 | 500-900 nit | LCSC/AliExpress, cheap | $5-12 | same outline concern as #2 |
| 4 | Waveshare 43H-800480-IPS (module w/ FPC driver board) | onboard converter (DSI) | DSI (not RGB) | 95.04×53.86 | 105.42×67.07 (display size), product 105.4×67.1 | "5mm thickness space" | 15-pin FFC to driver | n/a | Waveshare | ~$25-35 | DSI not RGB; driver board adds thickness; **rejected for final** (custom bridge required) but useful as bring-up reference |
| 5 | Newhaven NHD-4.3-800480EF-ATXL#-CTP class | EK9716B | 24-bit RGB | 95.04×53.86 | ~105.5×67.2 | ~2.8-3.5 | 40-pin 0.5 | 850 nit (CTP ver.) | distributor (US/EU), pricey | ~$30-45 | outline concern same; expensive |

Notes:
- ST7262E43 is the dominant driver IC in this class (800×480 RGB,
  DE/SYNC mode, 3.3 V logic, single 40-pin 0.5 mm FPC with LED-A/K on
  pins 1/2).  Pinout table for the Maclight part is public (pins
  1-2 backlight, 3 GND, 4 VDD 3.3 V, 5-12 R0-R7, 13-20 G0-G7, 21-28
  B0-B7, 29 GND, 30 PCLK, 31 DISP, 32 HSYNC, 33 VSYNC, 34 DE, 35 NC,
  36 GND, 37-40 resistive-touch NC when unused).
- **Backlight is the main electrical surprise**: 2 strings × 8 LEDs,
  IF=40 mA, VF=21.6-27.2 V (S043BWV106EP) — a boost LED driver is
  mandatory (stock PSP backlight was 7 LEDs ~24.5 V/18 mA, so the
  topology is familiar but current doubles).
- The 40-pin FPC pinout above is *panel-side*; the bridge PCB must
  mirror it correctly (see `docs/connector-orientation.md` when written).

## Fit assessment against the PSP front shell

| Item | Candidate value | Stock PSP | Verdict |
|---|---|---|---|
| Active area | 95.04×53.86 | 95.04×53.856 | exact match ✓ |
| Glass outline | 101.5-105.5 × 64.0-67.2 | 103.6×64.35 | borderline; CDTech 101.5×64.0 fits inside stock outline; Maclight 105.5×67.2 exceeds it |
| Module thickness | 3.0-4.53 (typ. with backlight frame) | 2.2 | exceeds; front shell expects ~2.2 glass — needs donor measurement of the aperture depth (U12) before committing |
| Interface | RGB 24-bit @ ~33 MHz pclk (800×480@60) | SVDI serial | simple; H618 has RGB outputs? **NO — H618 has HDMI/TV-OUT only**, hence the bridge (see system-architecture) |

## Decision (provisional)

- **Primary candidate: CDTech S043BWV106EP** (fits stock outline, public
  datasheet, 40-pin 0.5 FPC, standard ST7262E43 timing) — pending U12
  thickness measurement.
- **Backup: any LCSC-available ST7262E43 4.3" 800×480** with outline
  ≤103.6×64.35 confirmed from its 2D drawing before order.
- Bridge chip decision: **LT8619C** (Lontium, QFN76 9×9, HDMI 1.4 RX →
  24-bit RGB TTL up to 148.5 MHz DDR / 300 MHz SDR, on-chip EDID,
  datasheet archived at `docs/evidence/LT8619C_Datasheet_R1.4.pdf`)
  versus TFP401A (TI, through-hole-friendly breakout, 25-165 MHz, no
  scaler, needs external EDID EEPROM).  TFP401A is the debug/breakout
  choice; LT8619C is the compact final choice — both documented, no
  commitment made yet.

## Measurement requests created

- U12: front-shell aperture (window) and the depth available behind the
  glass for module + bridge PCB.
- U13: bezel lip width — does a cover-glass-extension panel hide the
  gap between 101.5 mm glass and the 103.6 mm window?
