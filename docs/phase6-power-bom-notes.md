# Phase 5/6 — Power board component selection (v0.1)

Status: working record for the power board schematic (Phase 6 start).
All parts verified to exist in the installed KiCad 10 symbol/footprint
libraries unless noted. Sourcing class: all catalog parts at major
distributors (VERIFIED_FROM_RELIABLE_SOURCE for function; exact ordering
is out of scope until Phase 8).

## USB-C input (5 V sink)

| Item | Part | Library ref |
|---|---|---|
| Receptacle | USB-C 16-pin USB 2.0, top mount | `Connector:USB_C_Receptacle_USB2.0_16P` + `Connector_USB.pretty:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` |
| CC pulldowns | 2x 5.1 kOhm 0402 (Rd on CC1/CC2) for default 5 V sink profile | passive |

Decision: no PD controller in v1 — the SBC needs at most 5 V/2 A (Radxa
ZERO 3W official requirement: 5 V/2 A). PD (9 V+) would add a controller
(STUSB4500) and higher-voltage ratings everywhere; deferred to v2 if
thermal measurements demand it.

## Charger / power path (1S Li-ion)

| Item | Part | Rationale |
|---|---|---|
| Charger + power path + OTG boost | TI `BQ25895RTW` (VQFN-20) | I2C-configurable, 3.9-5.5 V USB input? (see note), 5 V OTG output, power-path output SYS, BAT charge up to ~3 A; symbol `Battery_Management:BQ25895RTW`, footprint `Package_DFN_QFN.pretty:VQFN-20-1EP_3.5x3.5mm_P0.5mm_EP2x2mm` (verify datasheet footprint before Phase 6 layout freeze) |
| Battery protection | `DW01A` (SOT-23-6) + dual NMOS `Q_Dual_NMOS_G1S2G2D2S1D1` (8205-class, e.g. FS8205 footprint SOT-23-6) | overcharge/overdischarge/overcurrent cut-off, independent of the charger IC |

Input note: BQ25895 input range is 3.9-14 V with input current limit —
5 V USB-C direct is inside range. Verify the exact datasheet values
before committing ( datasheet must be downloaded and recorded in
docs/evidence/ before the schematic is finalized).

## Rails

| Rail | Regulator | Notes |
|---|---|---|
| SYS 3.9-5 V | BQ25895 power-path output | feeds downstream bucks |
| 3.3 V / 3 A | TI `TPS62130` (VQFN-16 3x3) | 3-17 V in, 0.9-6 V out, 3 A — SBC 3.3 V + logic; symbol `Regulator_Switching:TPS62130` |
| 5 V / 2 A | BQ25895 OTG mode (boost from BAT) | SBC 5 V rail; OR from USB-C 5 V through power path automatically |

5 V to the SBC comes from either USB-C 5 V (present) or OTG boost
(battery-only), switched inside BQ25895 — no extra ideal diode needed
between those two sources.

## Battery connection

- Connector: JST PH S2B-PH (2 pin) horizontal SMT — symbol
  `Connector_Generic:Conn_01x02`, footprint
  `Connector_JST.pretty:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal`.
  2.0 mm pitch, 2 A rating — OK for 1S charge/discharge currents here.
- Wiring rule (M4): the DW01A+MOSFET protection sits between the pack
  and the charger's BAT node; NTC wiring per U4 donor measurement.

## Open items before schematic freeze

1. Download BQ25895 datasheet into docs/evidence/, verify:
   input voltage range with USB-C 5 V, OTG output current (>= 2 A?),
   footprint name (VQFN-20 pin count / exposed pad size).
2. Download TPS62130 datasheet, verify 3.3 V/3 A thermal feasibility
   (inductor size vs shell height budget U1).
3. U4 donor measurement: battery connector pinout + thermistor presence.
4. Q6 decision recorded (own charger vs reuse S110 PMIC) — working
   assumption: own charger (console board fully removed).
