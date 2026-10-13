# BQ25895 pin map (from TI datasheet Table 6-1, primary source)

Extracted for the power board schematic (docs/evidence/BQ25895_datasheet_ti.pdf):

| Pin | Name | Type | Function |
|---|---|---|---|
| 1 | VBUS | P | Charger input (USB-C VBUS). 1 uF to PGND close to IC |
| 2 | D+ | AIO | USB D+ (BC1.2 detection) |
| 3 | D- | AIO | USB D- |
| 4 | STAT | DO | Charge status, open drain, 10k pullup |
| 5 | SCL | DI | I2C clock, 10k pullup |
| 6 | SDA | DIO | I2C data, 10k pullup |
| 7 | INT | DO | Interrupt, open drain, 10k pullup |
| 8 | OTG | DI | Boost enable (high + no VBUS -> OTG on) |
| 9 | CE | DI | Charge enable, active low |
| 10 | ILIM | AI | Input current limit set resistor (IINMAX = KILIM/RILIM) |
| 11 | TS | AI | Battery temperature (NTC bias from REGN) |
| 12 | / 13,14 | P | BAT - battery positive. 10 uF close to BAT |
| 15,16 | SYS | P | System output (power path). 20 uF close |
| 17,18 | PGND | P | Power ground |
| 19,20 | SW | P | Switching node (inductor). 0.047 uF bootstrap to BTST |
| 21 | BTST | P | High-side driver supply |
| 22 | REGN | P | LDO out 4.7 uF; also TS bias rail |
| 23 | PMID | P | Drain of RBFET/HSFET. OTG output. Caps: 8.2 uF (no OTG), 40 uF (OTG 2.4 A), 60 uF (OTG 3.1 A) |
| 24 | DSEL | DO | D+/D- mux select, 10k pullup |
| EP | PowerPAD | - | Exposed pad -> PGND plane, vias mandatory |

Design notes for the power board schematic:
- VBUS from USB-C VBUS (through no switch; CC pulldowns set 5 V sink).
- PMID ties to nothing external except caps (OTG output on VBUS internally
  through RBFET - check: OTG output appears on VBUS per datasheet; confirm
  in section 8.x before layout).
- SYS = input to TPS62130 buck (3.3 V/3 A) and SBC 5 V rail via load switch
  or direct (SYS 3.9-5 V operating range of the SBC must be verified
  against the Radxa ZERO 3W power input spec: 5 V +/- 5%? - open check
  against the v1.12 schematic PDF in cad/references/radxa-zero3w/).
- TS: NTC from pack (U4) or fixed 10k divider if pack has no thermistor.
- ILIM resistor: IINMAX = KILIM/RILIM, KILIM typ 390 uA*Ohm (min 320,
  max 425 per Electrical Characteristics - values 320/355/390 listed with
  min/typ/max). For 2 A: RILIM = 390u/2A = 195 ohm -> use 196 ohm 1%
  (verify with the actual table during schematic review).
