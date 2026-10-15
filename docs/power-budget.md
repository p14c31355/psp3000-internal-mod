# Power budget & topology v2

Updated: 2026-10-15.  Supersedes the v1 power-board README reasoning.
Numbers: typ/max from component datasheets where cited (class noted);
battery endurance is arithmetic, not measurement.

## 1. Loads (worst case)

| # | Load | Typ | Max | Class / source |
|---|---|---|---|---|
| 1 | OPi Zero 2W (H618 4-core A53 @1.5 GHz + LPDDR4 + WiFi) | 0.5 A @5 V | 2.0 A @5 V | VRS: official manual states 5V/2A supply; core load measured by community ~3-4 W peak — treat 10 W as ceiling |
| 2 | Panel logic (ST7262-class, 3.3 V) | 25 mA | 50 mA | datasheet-typical, VRS |
| 3 | Panel backlight (2×8 LED strings) | 80 mA @ ~24 V | 27.2 V / 80 mA | VERIFIED candidate datasheet (S043BWV106EP) |
| 4 | LT8619C bridge | 120 mA | 200 mA @3.3 V | datasheet brief, VRS |
| 5 | PSP motherboard (ARK mode only) | 0.4 A | 1.2 A @3.6-4.2 V | ESTIMATED — stock MB, no public number; U16 measurement planned |
| 6 | Supervisor + interposer (CH32V203 + TVS bias) | 10 mA | 30 mA @3.3 V | arithmetic |
| 7 | Audio amp (2×1 W class-D, future rev) | 150 mA | 500 mA peak @5 V | arithmetic |
| 8 | USB devices on OPi (host port, future) | — | 0.5 A | arithmetic |

## 2. Rail map (v2)

```
USB-C VBUS (5V, up to 3A)
   │
   ├────────────► BQ25895  ── PMID/VBUS-node ──► OPi 5V rail (mode: charge-pass / OTG-boost)
   │                 │                        ► panel 5V → 3.3V buck → panel+bridge logic
   │                 └ SYS = battery-follow  ► backlight boost (LED driver, PWM)
   │
battery pack (1S, DW01A + dual NMOS) ── SYS rail ──► PSP MB (ARK mode, stock path)
                                                     ► always-on 3.3V LDO → supervisor
```

- **Single VBUS-node architecture carried over from v1** (verified in
  v1 against the BQ25895 datasheet: OTG output emerges on the VBUS
  pin, so one node serves USB-C input and battery OTG).
- OPi power path: when USB-C is plugged, VBUS passes through the
  charger's pass-through; when on battery, BQ25895 boosts from SYS to
  5 V on the same node.  No OR-ing FET, no second converter for OPi.
  Boost capacity check: OTG spec 5 V @ 3.1 A ≥ OPi 2.0 A + panel
  ~0.5 A + bridge ~0.2 A = 2.7 A — inside spec with 0.4 A margin.
  That margin is thin but real; if U16 or bring-up shows the OPi
  pegging over 2 A sustained, the fallback is a dedicated TPS61023
  boost for OPi only (board space exists in option-B partition).
- PSP MB in ARK mode: stock MB runs from its own battery terminal —
  v2 keeps the pack terminal wired to the stock MB input, with the
  supervisor's load switch (backfeed-protected) only in the v2
  battery path.  Detail deferred to schematic: the stock MB expects
  to see the battery thermistor/ID lines — U17 measurement (pack ID
  behavior) needed before that interface is finalised.

## 3. Endurance arithmetic (honest numbers)

Battery pack: stock PSP-110-class 1200 mAh (3.7 V ≈ 4.4 Wh) — keep
removable, so this is the floor.

| Mode | Draw @ battery | Endurance (1200 mAh) |
|---|---|---|
| ARK (PSP MB + OPi + panel) | ~9 W | ~29 min — **the expensive mode** |
| Linux/Fullerene (OPi + panel) | ~6 W | ~44 min |
| PocketJS (light) | ~4.5 W | ~59 min |
| Charging while playing (USB-C 3 A) | net positive | indefinite |

ARK-mode endurance is poor because the OPi adds ~5 W of always-on
sink hardware for streamed video.  Mitigation options (rev 2, not
promised): dirty-rect streaming to cut OPi video work, or a 2-cell
power bank module in the UMD cavity (adds weight, keeps the PSP pack
for the MB alone).  Recorded as a known limitation with arithmetic,
not hidden.

## 4. Thermal

- BQ25895 charging at 3 A: ~1.5-2 W dissipation at thermal regulation
  near 5 V/3 A — the v1 board had it in open FR-4; v2 must place it
  near the battery bay edge with copper pour + thermal vias to the
  back-side ground (datasheet layout §layout recommendations).
- LT8619C at 33 MHz SDR: tens of mW — no thermal feature needed.
- Backlight boost: 24 V @ 80 mA from 5 V ≈ 0.5 W throughput, ~0.1 W
  loss — fine on 2-layer power section if the loop is tight.

## 5. Decisions recorded

- BQ25895 **retained** (charge + 3 A OTG + power-path in one 4×4 mm
  QFN; no cheaper single-part equivalent with OTG≥2.7 A exists in the
  JLCPCB Basic catalog — verified against the v1 datasheet analysis).
- DW01A + dual-NMOS pack protection **retained** from v1 (schematic
  blocks are reusable as-is; only placement changes).
- TPS62130 **retained** for panel/bridge 3.3 V buck (3 A ceiling gives
  margin; footprint proven in v1).
- New parts introduced by v2: backlight boost LED driver (candidate:
  TPS61165 / generic boost LED controller — decide in schematic
  phase), supervisor LDO (any 3.3 V 150 mA 2-layer LDO).
- LM2596S remains rejected (v1 decision stands: 150 kHz, large
  inductor, poor transient).
