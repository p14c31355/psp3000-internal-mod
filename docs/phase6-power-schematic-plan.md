# Power board schematic - KiCad generation plan (Phase 6 kickoff)

## Board: pcb/power-board/power-board.kicad_sch

Subcircuits (in dependency order):

1. USB-C input: `Connector:USB_C_Receptacle_USB2.0_16P`
   footprint `Connector_USB.pretty:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`
   - VBUS, GND, CC1/CC2 with 5.1k Rd each, D+/D- pass-through to charger,
     SHIELD to GND.
2. Charger: `Battery_Management:BQ25895RTW`
   footprint `Package_DFN_QFN.pretty:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm`
   - VBUS caps (1uF x2), PMID caps (60uF total for OTG), BAT cap 10uF,
     SYS cap 20uF, REGN cap 4.7uF, BTST-SW bootstrap 0.047uF,
     ILIM resistor 196R 1% (2A target), STAT/SCL/SDA/INT pullups 10k to
     3.3V logic, OTG pin to header (SBC GPIO), CE to GND (always enabled),
     TS divider (10k+10k NTC placeholder per U4), D+/D- straight from
     USB-C (BC1.2 detection by charger).
3. Battery protection: `Battery_Management:DW01A` (SOT-23-6) +
   `Device:Q_Dual_NMOS_G1S2G2D2S1D1` (SOT-23-6, 8205-class)
   - between BAT connector and charger BAT node: B- path, CS sense.
4. Buck: `Regulator_Switching:TPS62130`
   footprint `Package_DFN_QFN.pretty:VQFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm`
   - SYS in, 3.3V/3A out, FB divider, inductor 2.2uH (XFL4020-222MEB per
     TI reference), in/out caps per datasheet.
5. Battery connector: `Connector_Generic:Conn_01x02`
   footprint `Connector_JST.pretty:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal`
6. Output header to SBC: 2x03 2.54mm (5V, GND, 3.3V, OTG gpio, STAT,
   I2C SDA/SCL) - `Connector_Generic:Conn_02x05_Odd_Even` style.

## Generation method

Same as the SVDI breakout: Python generator extracting symbol definitions
verbatim from the installed KiCad libraries (renamed to lib-qualified
form), instances with uuid5-stable UUIDs, local labels + wires at real
symbol pin coordinates. Validation: kicad-cli sch erc must be 0 violations
before the PCB is generated.

## Symbol pin-coordinate map needed before generation

For each symbol: exact pin offsets from the .kicad_sym unit block (pin
at/length/name). The SVDI breakout generator hardcoded only Conn_01xNN
geometry; for BQ25895 (24 pins) the generator must parse pin positions
from the library file programmatically.

## ERC notes

- Every output pin must have a driver; power_in pins need PWR_FLAG on
  VBUS/SYS/BAT rails (2x `power:PWR_FLAG` symbols).
- BQ25895 symbol pin electrical types come from the library (passive/
  power_in/power_out etc.) - trust them.
