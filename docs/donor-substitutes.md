# Donor measurement substitutes - what the internet actually has

Updated 2026-10-13.  Goal: replace the U1-U5 physical measurements with
sourced data wherever possible, keeping the provenance classes honest.

## What was searched

- psdevwiki.com/psp/Motherboards (TA-090 = PSP-3000 03g board): revision,
  hackability, firmware history - no mechanical dimensions.
- psdevwiki.com/psp/SKU_Models: model/board matrix - no dimensions.
- westingames.com TA-090/093 pulled-motherboard listing: shipping box
  "17.8 x 8.0 x 1.3 cm" - that is the packaging, not the PCB; useful
  only as an upper bound (board must be < 178 x 80 mm), i.e. it merely
  confirms the obvious (board fits inside the 169.4 mm shell length).
- iFixit PSP 300x teardown: identifies TA-090, documents the strip-down
  sequence, but photos have no scale reference for measurement.

## Conclusion

No public source carries TA-090 PCB outline dimensions, mounting hole
positions, or component-keepout heights.  The donor measurements in
docs/MEASUREMENT-PLAN.md remain a physical task (STOP-condition item).

## What can be substituted today (non-dimensional)

1. Electrical donor data is partially covered by schematics floating
   around community repair forums, but none verified against a unit -
   treat any such schematic as UNVERIFIED, not as a source.
2. The enclosure constraint model can keep using the Sony-published
   body envelope (169.4 x 71.4 x 18.6 mm, VERIFIED_FROM_PRIMARY_SOURCE)
   plus the LCD glass outline from the Sharp LQ043T3LX02 datasheet
   (VERIFIED_FROM_PRIMARY_SOURCE).  Internal volumes stay UNKNOWN until
   measured, which the model already encodes via keepouts that only
   reference measured-outside surfaces.

## Proposed next step if a unit cannot be sourced

Buy a donor PSP-3000 board (pulled TA-090/093 boards are widely sold
for ~USD 10-20).  That single artifact unblocks U1-U3 (board outline,
holes, UMD cavity grid) and U5 (battery connector geometry) with
MEASURED provenance.  Purchasing is an owner decision (STOP condition:
payment required).
