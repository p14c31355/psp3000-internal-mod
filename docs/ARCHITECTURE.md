# Architecture and requirements — PSP-3000 internal SBC mod

Status: living document (v0.2, 2026-10-13). Owner: autonomous goal agent.
Constraint hierarchy: measured mechanical truth > electrical feasibility >
PCB convenience.

## 1. Objective

Rebuild the interior of a PSP-3000 as a Linux handheld:

- original PSP-3000 enclosure (external form preserved)
- original PSP-3000 LCD (Sharp LQ043T3LX0x) if technically feasible
- internal Linux-capable SBC (Radxa ZERO 3W class, RK3566)
- custom PCB(s) for power / LCD bridge / control translation
- USB-C power + data at the original bottom edge
- UMD door closes and latches with the UMD mechanism removed
- serviceable: disassembly does not require destructive shell work

## 2. Hard mechanical envelope (verified so far)

| Parameter | Value | Class | Source |
|---|---|---|---|
| Body W x D x H | 169.4 x 18.6 x 71.4 mm | VERIFIED_FROM_PRIMARY_SOURCE | Sony/SCEE official product overview |
| Weight (stock) | 189 g incl. battery | VERIFIED_FROM_PRIMARY_SOURCE | same |
| LCD module outline | 103.6 x 64.35 x 2.2 mm | VERIFIED_FROM_PRIMARY_SOURCE | Sharp LCM-09006 spec Table 5 |
| LCD active area | 95.04 x 53.856 mm | VERIFIED_FROM_PRIMARY_SOURCE | spec Table 5 |
| Battery PSP-S110 | 1200 mAh, 3.7 V Li-ion, 58.7 x 36.0 x 10.2 mm (nominal) | VERIFIED_FROM_RELIABLE_SOURCE | vendor battery listings; re-measure on donor |
| PCB thickness range in shell | UNKNOWN | UNKNOWN | needs donor measurement |
| UMD cavity free volume | UNKNOWN | UNKNOWN | needs donor measurement / 3D scan |

Everything downstream (board outlines, keepouts) must derive from a donor
measurement campaign (docs/MEASUREMENT-PLAN.md) — no nominal substitutions.

## 3. Subsystem requirements

### MUST

- M1: All boards fit inside original shell with lid closed; verified by
  STEP-vs-keepout interference check in FreeCAD before any layout freeze.
- M2: UMD door closes and latches; hinge swing unrestricted by internals.
- M3: Original LCD reused (target architecture; see Phase 4 decision record).
- M4: Battery charging via USB-C with protection; no unsafe battery wiring
  (protection IC or protected cell mandatory).
- M5: Original button matrix readable by the SBC (D-pad, action buttons,
  L/R, START/SELECT, analog stick pots, power switch).
- M6: Audio out to original speakers and headphone jack.
- M7: Every UNKNOWN dimension blocks dependent fit claims only — never gets
  silently replaced by a nominal value.
- M8: No ERC/DRC suppression without a documented, reviewed exception.

### SHOULD

- S1: SBC = Linux mainline (RK3566 has mainline U-Boot/Linux support).
- S2: SBC replaceable/upgradable without PCB respin (board-to-board or
  pin-header interface for the SBC).
- S3: Thermal: sustained SoC dissipation < 2 W; passive cooling only; no
  airflow paths (sealed shell).
- S4: Speakers driven by a class-D amp with I2C volume control.
- S5: Status LED + charging LED at original positions.
- S6: Debug: expose UART + USB during development; removable in final build.

### OPTIONAL

- O1: Wi-Fi via SBC onboard module (antenna placement review needed).
- O2: Vibration motor (original has none; skip unless trivial).
- O3: USB host exposed on original mini-USB footprint area (moved to USB-C).

### OPEN QUESTIONS

- Q1: Exact SVDI symbol packing (phase 4, requires donor capture or Samantha
  datasheet beyond panel spec).
- Q2: Internal height budget at each X/Y region (needs donor calipers +
  photos; FCC internal photos pending retrieval).
- Q3: Motherboard TA-090 screw boss / stand-off positions (donor measurement).
- Q4: Battery connector pinout and fuel-gauge behavior (donor measurement).
- Q5: Button matrix electrical map (membrane resistances; donor measurement).

## 4. Architecture (v0.2, after panel evidence)

```
                 USB-C (bottom edge, original jack footprint area)
                    |
        +-----------+-----------+
        |     POWER BOARD       |  buck-boost: 5V USB <-> 1S Li-ion
        |  - charge IC (1S)     |  battery protect + fuel gauge
        |  - 5V->3.3/2.5/1.8    |
        +-----------+-----------+
                    |
        +-----------+-----------+        +--------------------------+
        |     CONTROL BOARD     |  I2C   |  SBC (Radxa ZERO 3W)     |
        |  - button matrix scan |<------>|  - RK3566, eMMC, uSD     |
        |  - analog pot ADC     |        |  - USB OTG, uHDMI        |
        |  - audio amp 2xW      |        +--------------------------+
        |  - backlight boost    |                 |
        |  - panel rails        |                 | RGB888 parallel
        +-----------+-----------+                 v
                    |                    +--------------------------+
                    |   SVDI + rails     |  LCD BRIDGE (FPGA)       |
                    +------------------->|  - Samantha-equivalent   |
                                         |  - RGB888 -> SVDI TX     |
                                         +-----------+--------------+
                                                     | 31-pin FPC
                                                     v
                                            Sharp LQ043T3LX0x panel
```

Board count rationale (Phase 5 detail): the SBC must sit in the former UMD
cavity or atop the mainboard region; the LCD bridge belongs next to the
panel's FPC exit; power belongs at the bottom edge near the DC jack. A single
mega-board would fight the shell curvature; 2-3 small boards + flex ties is
the serviceable option. Final topology freezes only after Phase 2 keepouts.

## 5. Phase status

- Phase 0 (tooling audit): DONE — kicad-cli 10.0.7, kipy 0.8.0,
  freecadcmd 1.1.4, gate scripts proven (FAIL and PASS cases exercised).
- Phase 1 (this doc): IN PROGRESS.
- Phase 2 (mechanical truth model): BLOCKED on donor measurements (plan
  written first; see docs/MEASUREMENT-PLAN.md).
- Phase 4 (LCD feasibility): evidence collected, see docs/evidence/.
