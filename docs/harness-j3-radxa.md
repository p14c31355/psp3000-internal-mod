# J3 (power board) to Radxa ZERO 3W harness pin map

Updated: 2026-10-13.  Sources:

- Power board: `pcb/power-board/power-board.net` (J3 2x05 header nets,
  as routed).
- Radxa ZERO 3W 40-pin header: `cad/references/radxa-zero3w/radxa_zero_3w_product_brief.pdf`
  rev 1.12, section 6.1.1 (primary vendor source, table quoted below
  only where used).

## Radxa 40-pin pins this harness uses

| Radxa pin | Name | Function we need | Notes |
|---|---|---|---|
| 1 | +3.3V | (unused) | SBC's own 3.3 V regulator, do not back-feed |
| 2, 4 | +5.0V | 5 V rail input | "5V Power from the GPIO PIN 2 & 4" per product brief |
| 6, 9, 14, ... | GND | common ground | |
| 3 | I2C3_SDA_M0 (GPIO1_A0) | BQ25895 SDA | I2C bus 3 on the Radxa |
| 5 | I2C3_SCL_M0 (GPIO1_A1) | BQ25895 SCL | |
| 7 | GPIO3_C4 (PWM14_M0) | BQ25895 STAT interrupt sense (optional) | open-drain output on the charger side |

The Radxa's I2C3_M0 on pins 3/5 has on-board pull-ups on several Zero
models; the power board's R6/R7 (10k to REGN) may be left in place for
bench operation without the Radxa, but the harness document must flag
the parallel-pull-up question for the bring-up test plan (measure the
rise time with both pull-up sets installed).

## Power board J3 (2x05, 2.54 mm, as routed)

| J3 pin | Net | Goes to |
|---|---|---|
| 1, 2 | VBUS | Radxa pin 2 and 4 (+5.0V) |
| 3, 4 | GND | Radxa pin 6 and 9 (GND) |
| 5 | BAT | spare - battery voltage sense to SBC ADC (optional, Radxa SARADC) |
| 6 | GND | Radxa pin 14 |
| 7 | EN33 | Radxa pin 7 (GPIO3_C4) - future 3.3 V rail enable, defaults asserted |
| 8 | GND | Radxa pin 20 |
| 9 | STAT | Radxa pin 5 (I2C3_SCL_M0) is NOT used for this - see mapping note |
| 10 | GND | Radxa pin 25 |

## Mapping note / open question (U11)

STAT is the BQ25895 open-drain charge-status output.  Routing it to a
Radxa GPIO requires a free GPIO, and the natural pick would be pin 7
(GPIO3_C4), which is currently assigned to EN33.  Both fit on one
GPIO: STAT as an input with the Radxa's internal pull-up, and 3.3 V
rail enable strapped with a pull-up on the power board instead
(default-on).  Before finalising the harness:

1. confirm the Radxa GPIO3_C4 pull-up value tolerates the charger's
   open-drain STAT (5 V-tolerant check NOT needed - STAT swings to
   REGN 4.7 V, which exceeds the Radxa 3.3 V GPIO maximum: a level
   shifter or a 3.3 V-referenced divider is REQUIRED);
2. decide EN33 default state (strapped-on recommended).

U11 records the STAT level-shift requirement: REGN is 4.7 V, the
Radxa GPIO absolute maximum is 3.63 V.  Options: (a) divider
(2.2k/3.3k), (b) move STAT sensing to the SBC's SARADC channel as an
analog level, (c) open-drain with 3.3 V pull-up on the Radxa side and
remove R8's REGN pull-up on the power board (preferred - cheapest, and
STAT is open-drain so its pull-up rail defines the high level).

## Recommended resolution for U11

STAT: cut R8's REGN pull-up net (STAT net gets its high level from the
Radxa side 3.3 V through GPIO input pull-up), because the BQ25895 STAT
pin is open-drain and sinks only.  This is a one-line schematic change
plus re-route; scheduled for the next schematic revision.
