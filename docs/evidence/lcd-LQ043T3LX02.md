# Evidence: Sharp LQ043T3LX02 (PSP-3000 LCD panel)

Source of truth: Sharp LCM-09006 specification, "DEVICE SPECIFICATION FOR
TFT-LCD MODULE LQ043T3LX02", issued 2009-12-22, 45 pages.
Local copy: `docs/references/LQ043T3LX02_datasheet_sharp.pdf` (downloaded from
beyondinfinite.com library, 2026-10-13). Page references below use LCM-09006
page numbers (PDF page = spec page + 1).

Provenance class of everything in this file unless noted:
`VERIFIED_FROM_PRIMARY_SOURCE` (manufacturer spec sheet).

## Variants

- PSP-3000 shipped with Sharp LQ043T3LX01 .. LQ043T3LX03. This spec covers
  LQ043T3LX02; LX01/LX03 treated as same-family variants (community teardown
  evidence, `VERIFIED_FROM_RELIABLE_SOURCE`, retro report + panel vendor data).
- Panel family T-CON: Sharp "Samantha" LR388D7 / LR388G1. The 3000/Go panel
  uses LR388G1 (community evidence). The spec's drive recommendation and
  register tables assume a Samantha part on the HOST side.

## Mechanical (spec Table 5)

| Item | Value |
|---|---|
| Screen diagonal | 10.9 cm (4.3 in) |
| Active area | 95.04 x 53.856 mm |
| Pixels | 480 x 272 (RGB stripes) |
| Pixel pitch | 0.198 x 0.198 mm |
| Outline (no FPC/projections) | 103.6 x 64.35 x 2.2 mm |
| Mass | 23 g typ |
| Display mode | Normally black, mobile ASV |

FPC placement (spec 6-1): backlight FPC terminates on the BACK side, LCD FPC
on the FRONT side.

## LCD FPC pin map (spec Table 6-3, 0.5 mm pitch, 31 pins)

| Pin | Name | Dir | Function |
|---|---|---|---|
| 1 | COM | I | Common electrode drive (VCOM) |
| 2 | PNL | O | Panel control signal |
| 3 | NC | - | |
| 4 | VGL | P | TFT gate OFF voltage |
| 5 | NC | - | |
| 6 | VGH | P | TFT gate ON voltage |
| 7 | VL | P | Gamma ref low (=GND allowed) |
| 8 | VH | P | Gamma ref high |
| 9 | GND | - | |
| 10 | VS | P | Source driver analog power |
| 11 | VS | P | (twin) |
| 12 | GND | - | |
| 13 | VCC | P | Logic power 1.8 V |
| 14 | SDO | O | Serial data out |
| 15 | SDI | I | Serial data in (register port) |
| 16 | SCLK | I | Register clock (<=12.5 MHz) |
| 17 | SCS | I | Register chip select |
| 18 | REV | O | Polarity inversion signal |
| 19 | RESETB | I | Reset |
| 20 | GNDRX | - | Diff GND |
| 21 | DATA2+ | I | Diff pair DATA2 |
| 22 | DATA2- | I | |
| 23 | GNDRX | - | Diff GND |
| 24 | CLK+ | I | Diff pair CLK |
| 25 | CLK- | I | |
| 26 | GNDRX | - | Diff GND |
| 27 | DATA1+ | I | Diff pair DATA1 |
| 28 | DATA1- | I | |
| 29 | GNDRX | - | Diff GND |
| 30 | VCCRX | P | Diff block power 1.8 V |
| 31 | COM | I | Common electrode drive (twin) |

## Backlight FPC (spec Table 6-2, 0.5 mm pitch, 4 pins)

| Pin | Name | Function |
|---|---|---|
| 1 | VLED- | LED cathode |
| 2 | NC | |
| 3 | NC | |
| 4 | VLED+ | LED anode |

Backlight: 7 LEDs, series chain. Ratings (spec 7-1 / 8-1): ILED max 35 mA
(Ta=25C), PLED max 130 mW per LED; recommended ILED 18 mA typ; voltage across
VLED+/GND up to 24.5 V max. => Needs a series LED boost driver ~20-25 V,
18-20 mA. PWM dimming on the enable/anode path is the standard approach
(Samantha drives it via a PWM register bank; a host MCU can do the same).

## Power rails (spec 7-2 / 8-2, all generated HOST-side by Samantha)

| Rail | Min | Typ | Max | Note |
|---|---|---|---|---|
| VCC | 1.65 | 1.8 | 1.98 | logic; tie to VCCRX |
| VCCRX | 1.65 | 1.8 | 1.98 | diff block |
| VS | 5.4 | 5.6 | 5.7 | source driver analog |
| VGH | 15.9 | 16.5 | 17.1 | gate ON |
| VGL | -11.4 | -11.0 | -10.6 | gate OFF |
| VH | 2.0 | 4.5 | VS-0.2 | gamma high |
| VL | GND | GND | VS-2.0 | gamma low |
| VCOMpp | 4.2 | 4.3 | 4.4 Vpp | COM drive amplitude |

Current consumption (spec Table 8-4, VCC=1.8, VS=5.6, VGH=16.5, VGL=-11.0):
IVCC 1.6 mA typ / 3.0 max; IVCCRX 1.7 / 2.5; IVS 2.1 / 5.0; IVGH 0.1 / 0.4;
IVGL 0.1 / 0.3. Total panel-side rail power is tiny (< 50 mW); the
significant power is the backlight (~24 V x 18 mA = ~0.45 W).

Power sequencing (spec p.13): VCC,VCCRX ON -> RESETB release -> VGL ->
VLS,VH,VGH. Reverse on shutdown. Full register-driven ON/OFF sequences in
spec Appendix 2/4.

## Video interface: SVDI (Sharp proprietary LVDS-like)

- Spec Table 9-1: 3 differential pairs total: CLK+, CLK- and DATA1+, DATA1-
  and DATA2+, DATA2- on the LCD FPC. "SVDI operating frequency (2ch both
  edges)" 48 / 54 / 60 MHz min/typ/max. Data valid window 2.5 ns, setup/hold
  1.2 ns -> source-synchronous DDR sampling on both edges.
- Common mode 0.5xVCCRX, differential amplitude >= 80 mV (spec Table 8-3).
- Diff pair routing requirements (Appendix 3 notes): 50 ohm single-ended,
  ~100 ohm differential, intra-pair skew minimized, GNDRX guard.
- 480x272 @ 60 Hz needs ~9.44 Mpx/s x 24 bit = 227 Mbit/s user payload; over
  2 data pairs DDR at 54 MHz that is 216 Mbit/s raw -> framing overhead is
  nearly zero; expect ~6 pixels per (DATA1,DATA2) 2-channel beat with
  start/stop code frames.

## Register/sequencing interface (host side, via SDI/SCLK/SCS)

Spec Appendices 1-4 give the full Samantha register map used with this panel:
- Basic timing: HSYNC width 0x29, HBP 2, H valid 0x78 (=120 -> x4 units =
  480 px), HFP 2; VSYNC 2, VBP 2, V valid 0x44 (=68 -> x4 = 272 lines),
  VFP 4.
- PLL: x4 multiplier + division tree.
- SVDI TX framing registers (A2-1 steps 38-60): V start code 32-bit
  VF=FF000003h, H start code HF=FF000005h, V end VE=FF00000Ah,
  H end HE=FF000009h; syntyp=01, TXVDBUF0=40h, TXVDBUF1=80h.
- Power-tree registers: VREF/OSC/VDC2A/VDC2B/VGL/VGH boost control with
  10 ms settling steps.
- 24-bit parallel RGB input mode (IMGBUS=000, Appendix 4) and 8-bit serial
  mode (6-bit x 3, IMGBUS=010, Appendix 2) both documented with full
  register write sequences.
- Backlight PWM bank (REFh=0, R6Ah polarity, R68h SHDN states) documented.

## Consequences for the mod

1. The panel is a RECEIVING device: it needs a Samantha-equivalent host that
   (a) accepts 24-bit parallel RGB, (b) transmits SVDI at 48-60 MHz DDR with
   the framing codes above, (c) generates VS 5.6 V / VGH 16.5 V / VGL -11.0 V
   / VCOM / gamma rails, (d) sequences power and registers, (e) drives
   backlight PWM.
2. No commodity converter chip speaks SVDI (Sharp proprietary, used only in
   PSP-2000/3000/Go class devices). Reuse of the original 3000 panel therefore
   requires an FPGA (or equivalent) implementing the TX side, OR recovery of
   the host-side SVDI bit stream from a donor console for protocol capture.
3. The register tables above are sufficient to enumerate WHAT must be done;
   the exact SVDI symbol packing (which bits go on DATA1 vs DATA2, code
   insertion alignment) is NOT in the panel spec -> tracked as UNKNOWN in
   docs/UNKNOWNS.md.
