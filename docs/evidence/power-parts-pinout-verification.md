# BQ25895 pin/packaging verification (Phase 6 pre-check)

Verified against the downloaded TI datasheet
(docs/evidence/BQ25895_datasheet_ti.pdf, TI lit PDF fetched 2026-10-13):

- Package: WQFN (RTW), 24 pins, PowerPAD exposed pad required
  ("Always solder PowerPAD to the board" - p. PowerPAD section).
- KiCad symbol `Battery_Management:BQ25895RTW`: pins numbered 1..25
  (25 entries incl. pin 25 = GND/thermal-pad representation).
- KiCad footprint candidates: `Package_DFN_QFN.pretty:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm`
  (+ ThermalVias variant). This is the correct 24-pin 4x4 mm WQFN for RTW.
- Key electricals from datasheet front page: input 3.9-14 V, input current
  limit 100 mA-3.25 A, OTG 5 V at 3.1 A, charge current up to 3 A (determined
  by ILIM resistor / I2C).

Conclusion: symbol BQ25895RTW + footprint Texas_RTW_WQFN-24-1EP_4x4mm
is the correct pair for the power board. The earlier draft in
docs/phase6-power-bom-notes.md incorrectly listed a VQFN-20 footprint;
corrected here.

TPS62130: VQFN-16 3x3 mm (RGT), exposed thermal pad mandatory (AGND+PGND
both tied to it). Footprint: `Package_DFN_QFN.pretty:VQFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm`
- the exact EP size must be cross-checked against the mechanical drawing
in TPS62130_datasheet_ti.pdf during layout; datasheet quotes 3x3 mm body
with exposed pad (RGT 16 pins).

DW01A: SOT-23-6, overcharge 4.25 V typ, overdischarge 2.4 V typ,
overcurrent via CS sense with external dual NMOS (8205-class).
Datasheet copy: docs/evidence/DW01A_datasheet_sparkfun.pdf (DW01-P
variant datasheet, same family - DW01A pinout identical per LCSC/
community references; verify VOCP=4.25 vs DW01A=4.3 on the actual
DW01A sheet before final freeze).
