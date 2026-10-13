# Phase 5 — Power architecture (working notes, v0.1)

Status: evidence-based notes only. Final schematic waits on U4 (battery
connector pinout) and donor measurements. No battery wiring may be copied
without validation (MUST M4).

## Key prior art (VERIFIED_FROM_RELIABLE_SOURCE, hackaday 2014 teardown)

Source: hackaday.com "Replacing the Li-Ion Cells of the PSP Battery"
(Cristi Caciuloiu, 2014-09-19) — local copy not saved; quotes verified
against the fetched text 2026-10-13.

Facts established by that teardown:

1. The PSP-S110 battery pack contains its own power-management PCB
   (10-pin design on generics; original Sony uses a custom PMIC labeled
   `16808C18SC`, believed an NEC design or custom ASIC with charge control
   + fuel gauge + authentication).
2. The PSP console refuses generic packs whose PMIC is not Sony-compatible:
   generic packs worked briefly, then died under the PSP's charging pulse
   pattern, and were no longer recognized nor charged.
3. A donor cell (Canon NB-6L, 3.7 V prismatic with tiny protection board
   removed) transplanted into an ORIGINAL S110 management PCB kept all
   console functions: charge-level reporting in the system menu, USB
   charging, low-battery auto-standby.
4. The pack connects to the console through an external power socket
   (plug) on the battery PCB, not a soldered wire harness.

## Consequences for our design

- The battery, its PMIC, and the console form a proprietary system
  (authentication + charge pulses). Re-inventing that interface is
  high-risk; reusing an ORIGINAL PSP-S110 management PCB with a fresh
  protected cell is the proven path (M4 satisfied by the pack's own
  protection + the console's own charger).
- Our SBC subsystem therefore does NOT need its own charger if it
  coexists with the original PMIC; it needs:
  a) a fused, current-limited tap from the pack's output (VBAT→SBC buck),
  b) its own USB-C input ONLY if we want the SBC to run/charge with the
     console electronics removed — decision OPEN Q6,
  c) reverse-polarity protection on the tap (series P-FET or Schottky),
  d) power-path architecture: where does the SBC's 5 V USB-C input meet
     the pack's 3.7-4.2 V? Ideal-diode OR-ing or a dedicated buck-boost
     with power-path (e.g. BQ25895-class or MPS MP2615-class + buck).

## Open questions created

- Q6: Does the mod keep the original console power board at all, or is
  the SBC the only consumer? If the PSP motherboard is fully removed
  (our architecture), the "PSP charging pulse / authentication" concern
  disappears and we own the whole battery interface — then a proper
  1S charger + protection (BQ25895/DW01A+FS8205 class) is MANDATORY and
  the S110 PMIC question is moot. DEFAULT working assumption: full
  removal, we own the pack contacts (P+, P-), so we need our own charger.
- Q7: If we own the pack: does the S110 connector expose a thermistor?
  Donor measurement m2.1 (docs/MEASUREMENT-PLAN.md) answers this. The
  charger's NTC input must be wired per measurement, or the charger must
  be configured for fixed temperature window.

## Proposed subsystem (to be finalized after Q6/Q7)

```
USB-C (CC1/CC2 5.1k Rp for default 5V sink; optionally PD via STUSB4500)
  → fuse 2A → BQ25895-class 1S charger (power-path, OTG out 5V)
      BAT+ → pack P+ (through measured connector)
      BAT- → pack P-   TS → NTC (per U4 measurement) or fixed divider
  → SYS 3.9-5V (power path output) →
      buck 3.3V 3A → SBC 3.3V rail + logic
      buck 5V/2A   → SBC 5V rail (GPIO power, USB host)
      buck 1.8V    → panel rails (via LCD bridge board)
  Battery-only mode: BQ25895 OTG boosts pack → SYS 5V.
```

Reverse-polarity / reverse-current: BQ25895 has internal reverse blocking
on BAT; add a P-FET on the pack tap for belt-and-braces per M4 review.

## Next actions

1. m2.1 donor measurement (battery connector pinout incl. thermistor).
2. Decide Q6 (own charger vs reuse S110 PMIC) — this is an architecture
   decision; if owner preference is split, raise as a stop-condition
   question with evidence (this note).
3. Then schematic the power board in KiCad on this branch.
