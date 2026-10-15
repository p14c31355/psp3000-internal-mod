# System architecture v2 — dual-personality PSP-3000

Updated: 2026-10-15.  Branch: `feat/v2-system-redesign`.
Predecessor: `docs/ARCHITECTURE.md` (Radxa-based, Phase 0-7) — kept as
reference, superseded by this document.

## 1. Requirements recap (owner-approved)

- PSP-3000 body, externally stock.  UMD drive permanently removed;
  door stays shut as exterior.  Internal UMD-support plastic may be
  cut (protected list: perimeter, screw bosses, hinge, latch, speaker
  mounts, structural ribs, battery structure).
- SBC: **Orange Pi Zero 2W** (H618, 65×30×1.2, 4×3.0 mm holes,
  5V/2A).  Radxa substitution forbidden unless proven blocked.
- 4 personalities, selected **without opening the UMD door**, selection
  survives power cycles, documented state machine:
  1. ARK-4 / native PSP
  2. Linux (OPi)
  3. FullereneOS (OPi)
  4. PocketJS (OPi)
- Display: generic 4.3" 800×480 RGB panel (see display-candidates.md).
- Input: original PSP controls usable in all 4 personalities.
- Retain removable PSP battery + external charging.

## 2. Display datapath (decided)

H618 exposes **HDMI 1.4 + CVBS only — no parallel RGB**.  Therefore:

```
H618 HDMI ──> LT8619C (HDMI RX, QFN76 9×9) ──> RGB888 24-bit ──> ST7262E43-class 4.3" panel
                    │ on-chip EDID (no EEPROM)
                    └ I2C control (auto-config, defaults OK)
```

- LT8619C auto-reads the panel timing from I2C registers; with the
  panel fixed at 800×480@60 the receiver can be register-initialized
  by the supervisor MCU at power-on (or left in default mode after
  one-time config) — TBD in schematic phase, datasheet archived.
- TFP401A remains the debug-breadboard choice (through-hole friendly),
  not the final board.
- PCLK for 800×480@60 ≈ 33 MHz — far below the 148.5 MHz DDR limit;
  SDR RGB output at 33 MHz is comfortably in spec, 3.3 V TTL.
- FullereneOS: the bridge is *dumb* (no framebuffer), so any OS that
  can output HDMI at a fixed 800×480@60 mode drives the panel
  unchanged.  H618 BSP must add a 800×480@60 HDMI mode — kernel work,
  tracked, not hardware-blocking.

## 3. ARK / native PSP video datapath (investigation item, not decided)

Original PSP motherboard drives its own LCD over SVDI (serial, DDR
48-60 MHz) to the LR388G1 T-CON — the replacement panel cannot accept
this.  Candidate paths for ARK video on the new panel:

| Path | Latency | Throughput | Complexity | Verdict |
|---|---|---|---|---|
| A. ARK PRX framebuffer streaming over USB to OPi (RemoteJoy-class) | ~2-4 frames (USB 2.0 + memcopy) | 480×272×2 B×60fps = 15.7 MB/s (raw); dirty-rect typically <5 MB/s | software: ARK PRX + host reader | **primary investigation**; bandwidth trivially fits USB 2.0 (480 Mbps ≈ 40+ MB/s effective) |
| B. FPGA captures SVDI serial → converts to RGB | <1 frame | full | large FPGA, SVDI protocol reverse-eng | rejected for rev 1 (owner: only if USB path fails) |
| C. Native PSP screen kept for ARK, new panel for OPi only | 0 | n/a | two displays, stock T-CON | fallback; conflicts with "replace the LCD" requirement — rev 2 contingency only |

**Documented limitation (accepted by owner for rev 1):** PSP boot
graphics before the ARK streaming PRX starts will not appear on the
replacement panel.  Bandwidth numbers above are calculations, not
measurements — the PRX does not exist yet; this is the largest
software risk of the project and is tracked, not claimed solved.

## 4. Input architecture (direction)

PSP button FPC carries a **matrix**, not per-button GPIO (measurement
U14 pending: exact row/col count and pull locations).  Architecture:

```
PSP button FPC ──> input interposer PCB (passes through to PSP MB unchanged)
                        └ high-Z observation taps ──> supervisor MCU (CH32V203-class)
                                                          └ UART ──> OPi (and to host SW in ARK mode)
```

- Pass-through preserves native PSP/ARK operation with zero latency.
- MCU observes the matrix scan passively (buttons are active-low rows/
  columns with pull-ups on the PSP MB — verified logic direction
  pending U14), detects presses, forwards over UART at 115200 8N1
  with a 12-byte fixed frame (button bitmask + stick X/Y + seq).
- CH32V203 (QFN-28, ~$0.50, JLCPCB Basic family) chosen over RP2040:
  sufficient for matrix scan + UART + supervisor FSM, 10× cheaper,
  smaller.  RP2040 only if USB HID device class is later required.

## 5. Supervisor / boot selection

Supervisor = the input MCU (one chip, two roles).  State machine:

```
states: OFF → POWER_ON → MODE_CAPTURE → MODE_LATCH → RUN(mode) → SHUTDOWN_REQ → OFF
```

- POWER_ON: user slides PSP power switch.  Supervisor powers itself
  from always-on battery rail (DW01A-protected pack, ~µA draw), arms
  rail switches.
- MODE_CAPTURE: for 1.5 s after power-on, supervisor samples the
  button matrix; combos:
  - no combo → last latched mode (survives power cycle, stored in
    MCU flash/EEPROM emulation)
  - HOME+Left = ARK, HOME+Up = Linux, HOME+Right = FullereneOS,
    HOME+Down = PocketJS (exact combo TBD — these are the documented
    defaults, not sacred)
- MODE_LATCH: writes mode to flash, sets OPi boot choice GPIO strap
  (2 bits to OPi GPIO read by its boot script/U-Boot), powers OPi
  rail + panel backlight per mode:
  - ARK: OPi ON (video stream sink) + PSP MB ON
  - Linux/Fullerene/PocketJS: OPi ON, PSP MB stays OFF (battery life,
    no coexistence hazards), panel ON
- RUN: supervisor services safe-shutdown request (power switch slide
  again = graceful `poweroff` request to OPi via UART, wait for ACK,
  cut rails), watchdog on OPi heartbeat (optional, rev 2).
- OFF: all switchable rails off; supervisor in ~2 µA sleep.

Mode strap to OPi: 2 GPIO bits + strobe, read by an initramfs script
that kexecs/pivots to the chosen OS (Linux↔FullereneOS↔PocketJS) or
idles for ARK streaming.  This keeps U-Boot untouched (one kernel,
four personalities) — no bootloader modification required, documented
as the mechanism until proven otherwise.

## 6. Power budget (worst case, draft)

| Rail | Load | Typ | Max | Notes |
|---|---|---|---|---|
| VBUS 5V (USB-C in) | charge + system | — | 3.0 A | BQ25895 input limit / ILIM |
| SYS (battery-follow) 3.7-4.2V | everything below | — | — | single-battery architecture |
| OPi 5V | H618 + RAM + WiFi + USB | 0.8 A | 2.0 A | boost from SYS (TPS61023-class) or VBUS pass-through when charging |
| Panel VDD 3.3V | logic | 30 mA | 50 mA | buck or LDO from 5V rail |
| Backlight | 2 strings × 8 LED | 40 mA ×2 | 27.2 V / 80 mA total | boost LED driver (TBD part), PWM dim by supervisor |
| HDMI bridge 3.3V/1.8V | LT8619C | 120 mA | 200 mA | from panel rail |
| PSP MB 3.6V rail (ARK mode) | stock MB | ~0.5 A | 1.2 A | stock regulator path, fed from SYS |
| Supervisor+input MCU | 3.3V | 10 mA | 30 mA | always-on from SYS via LDO |
| Audio amp 5V | 2×1 W class-D | 150 mA | 400 mA peak | TBD part |
| **Total SYS draw** | | | **≈ 4.0 A peak (rare), 2.5 A sustained** | PSP battery (1200-1800 mAh) sustains ~1 h heavy / 2-3 h typical — acceptable for rev 1, honest number |

Charging: BQ25895 retained from v1 (single-cell, 3A, VBUS-OTG powers
OPi when unplugged — the single-VBUS-node architecture carries over).
Its sizing is re-justified: OTG 5V/3.1A exactly covers the OPi+panel
peak; no cheaper part does charge+OTG+path in one package at this
size.  DW01A+FET pack protection retained.

## 7. Partitioning (decision pending mechanical study)

| Option | Boards | Pros | Cons |
|---|---|---|---|
| A | power+supervisor | display bridge | 2 boards, each simple; bridge sits behind panel; power sits near battery |
| B | power | supervisor/input | display bridge | 3 boards: input interposer is FPC-adjacent anyway |
| C | single | fewest connectors | board must span from battery bay to display — long, irregular, conflicts with UMD cavity shape |

Leaning **B** (input interposer must physically live at the button
FPC; display bridge must live at the panel FPC; power lives at the
battery bay — three mechanical anchors, forcing three boards, but two
of them are tiny).  Final call after `docs/mechanical-layout.md`.

Interconnects: 8-12 pin 0.5 mm FFC (power↔bridge, power↔supervisor),
all low-speed (I2C/UART/rails) except none — no high-speed crosses a
board boundary.  HDMI stays entirely on the bridge board.

## 8. Open items blocking schematic start

- U12 (panel aperture depth) — drives whether 3.0-4.5 mm module fits.
- U14 (button FPC pinout/matrix map) — drives interposer design.
- OPi Zero 2W hole positions (ESTIMATED 3.5 mm inset) — donor board
  measurement when available; 3.0 mm hole diameter is VERIFIED.
- OPi 24pin FFC pinout image read (primary image saved, pending
  reliable vision pass) — needed before the harness connector is
  chosen.
