# Phase 3 — SBC candidates and integration model

Status: v0.1 (2026-10-13). Placement decisions are BLOCKED on U1-U3; this
file records candidates and their hard data only.

## Candidate 1: Radxa ZERO 3W (primary candidate)

| Attribute | Value | Class | Source |
|---|---|---|---|
| SoC | Rockchip RK3566, 4x Cortex-A55 @1.6 GHz, Mali-G52-2EE | VRS | Radxa docs |
| RAM | 1/2/4/8 GB LPDDR4 | VRS | Radxa docs |
| Storage | onboard eMMC 8-64 GB + microSD | VRS | Radxa docs |
| Board size | 65 x 30 mm | VRS | Radxa docs + vendors |
| USB | 1x USB-C 2.0 OTG (power/data), 1x USB-C 3.0 host | VRS | Radxa docs |
| Display | micro HDMI 1080p60 | VRS | Radxa docs |
| CSI | 1x 4-lane MIPI CSI (22-pin 0.5 mm) | VRS | vendor page |
| Wireless | Wi-Fi + BT (5.0/5.4 per doc/vendor variance) | VRS | Radxa docs |
| GPIO | 40-pin: UART/SPI/I2C/I2S/PWM | VRS | Radxa docs |
| Power | 5 V input, 1-2 A class | VRS | Radxa docs (5V/2A adapter rec) |
| Linux | Debian/Ubuntu; RK3566 mainline U-Boot/Linux supported | VRS | Radxa docs, community |
| Component height (top side) | UNKNOWN | UNKNOWN | board photos/drawing needed |
| Mounting hole positions | UNKNOWN | UNKNOWN | mechanical drawing needed |
| Availability | in distribution (multiple vendors) | VRS | vendor pages |

Fit observation (preliminary, not a placement claim): 65x30 mm fits inside
the 169.4x71.4 body envelope; the binding constraint is HEIGHT (U1) around
connectors (USB-C, micro-HDMI) and the 40-pin header if populated. The
40-pin header can stay unpopulated on the shell side if our carrier
interface is custom.

## Evaluation criteria (frozen for comparisons)

1. fits height budget at candidate regions (after U1)
2. mainline Linux (no vendor kernel fork dependency)
3. display path compatibility with Phase 4 bridge (RGB parallel out via
   GPIO DPI-class pins or MIPI DSI would need extra HW)
4. USB-C data for gadget/OTG modes
5. power draw <= 2 W sustained
6. sourcing: orderable in single quantities, no NDA blockers

## Open issue: RGB parallel output from RK3566

The Phase 4 bridge expects 24-bit RGB888 + syncs input (Samantha-style).
RK3566 exposes an RGB parallel LCD controller (VOP + LVDS/RGB pins) on some
carrier designs, but the ZERO 3W pins out micro-HDMI and MIPI CSI instead.
Options to resolve in Phase 5:
- use RK3566 RGB-capable alternative SBC/SOM,
- use USB/HDMI-to-RGB conversion (adds latency/complexity), or
- reconsider bridge input as HDMI->SVDI (FPGA receives TMDS, not RGB).
Decision deferred until U6 (SVDI packing) is closed; do not commit hardware.

## Rejected / deferred candidates (log)

- Raspberry Pi Zero 2 W: DPI GPIO possible, but 512 MB RAM + older core;
  PSPi project proves the form factor. Keep as fallback.
- Orange Pi Zero class: weaker mainline display support.
- Luckfox / Milk-V class: no display controller path for RGB888.
