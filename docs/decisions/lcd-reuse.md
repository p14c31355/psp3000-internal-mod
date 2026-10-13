# Phase 4 decision record — original LCD reuse

## Context

PSP-3000 panel = Sharp LQ043T3LX01..03 (see docs/evidence/lcd-LQ043T3LX02.md).
The panel integrates only the panel-side RX of Sharp's proprietary SVDI
serial video link and needs host-generated rails (VS/VGH/VGL/VCOM/gamma).
In the stock console those functions live in the "Samantha" T-CON
(LR388D7/LR388G1) on the motherboard — which the mod removes.

Therefore "reuse the original LCD" == "reimplement a Samantha-equivalent
host": 24-bit RGB in -> SVDI TX out (54 MHz DDR, 3 diff pairs, framing
codes VF/HF/VE/HE documented) + boost/regulator tree + register sequencer +
backlight PWM.

## Options

| # | Option | Pros | Cons | Verdict |
|---|---|---|---|---|
| A | FPGA bridge implementing SVDI TX + rail sequencing (own board) | keeps original panel; no shell face change; fully ownable | SVDI symbol packing UNKNOWN (U6) -> protocol capture or Samantha datasheet required; FPGA on dense board in tight shell | candidate (blocked on U6) |
| B | Recover + reuse the donor's Samantha T-CON subsystem on a carrier board | protocol solved by construction (real chip) | requires desoldering BGA-class part or harvesting a sub-board from a second donor; long-term sourcing risk; Spike reverse effort still needed for register sequencer host | fallback |
| C | Replace panel with a commodity 480x272 RGB888 parallel panel (e.g. the PSPi-class 4.3" 800x480 or 480x272 panels) | trivial interface; proven by PSPi project | departs from "original LCD" MUST (M3); front bezel/laminate differences | rejected unless A and B both fail |
| D | iCoupler/LVDS serializer hack (generic LVDS chip) | cheap | generic chips do not speak SVDI framing; dead end | rejected |

## Decision

PROVISIONAL: Option A (FPGA bridge) is the target architecture, gated on
evidence campaign 3 (SVDI capture, docs/MEASUREMENT-PLAN.md). Option B is
the fallback if capture fails. Option C is the failure path — it would
require amending MUST item M3 with owner approval (stop condition: owner
preference decision).

No work claiming a working bridge exists before U6 is closed. DRC/ERC and
STEP gates apply to the bridge board like any other.

## Sourcing notes

- LR388G1: not distributed; appears only on PSP motherboards.
- Panel: LQ043T3LX03 new/used from panel vendors ($18-45 class, community
  data, VERIFIED_FROM_RELIABLE_SOURCE).
- FPGA candidate class: Lattice ICE40UP5K / ECP5-12F or Gowin GW1N/LV —
  final pick in Phase 6 with pin budget (RGB888 24 + DE/HS/VS/CLK in,
  3 diff pairs out, SPI, rails enable).
