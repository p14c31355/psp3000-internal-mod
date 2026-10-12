# Radxa ZERO 3W power input verification (primary source, v1.12 schematic)

Source: cad/references/radxa-zero3w/radxa_zero_3w_v1.12_schematic.pdf
(text extracted 2026-10-13).

Findings:

- The board takes a single `+5V_INPUT` rail, fed from (a) the USB-C
  receptacle VBUS (`J2 USB_TYPEC_115H0`, sheet shows A7/B7 VBUS pins) and
  (b) GPIO header pins 2/4 (with a 10 uF cap and a 0-ohm link R39 nearby).
- The PMIC is `RK817-5` (PMIC+Codec), block named "5V DC IN" -> "PMIC+Codec".
- No wide input range on the board itself: whatever supplies +5V_INPUT
  must be a regulated 5 V (the RK817 takes the 5 V directly).

Consequence for our power architecture (RESOLVED against the BQ25895
datasheet):

- OTG boost output appears on **VBUS** ("the VBUS output is 5V by default"
  during boost mode, datasheet p. boost-mode section) - NOT on PMID.
  PMID is the boost input node (drain of RBFET/HSFET).
- Therefore the SBC 5 V rail should be fed from **VBUS**: USB-C present ->
  VBUS is 5 V input; battery-only + OTG enabled -> VBUS is 5 V boost
  output. One node, both modes, no OR-ing FETs needed.
- SYS (3.5-4.85 V range, follows BAT) feeds only the 3.3 V buck
  (TPS62130, input range 3-17 V - compatible).
- PMID capacitance: 60 uF minimum for OTG 3.1 A (we need ~2 A -> 40 uF
  minimum; design 60 uF for margin).
- OTG pin driven by SBC GPIO (or pulled high with a jumper for
  battery-only operation).
- Recorded as the resolution of the "SYS voltage range vs SBC input" open
  check in bq25895-pinmap.md: option A confirmed by datasheet (OTG 5 V on
  VBUS for SBC; SYS only for the 3.3 V buck).
