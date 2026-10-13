#!/usr/bin/env python3
"""Generate the power board KiCad schematic (Phase 6), staged.

Stage 1: USB-C receptacle + CC pulldowns + PWR_FLAG (ERC-clean shell)
Stage 2: + BQ25895 charger core
Stage 3: + DW01A/Q1 battery protection + J2 battery connector
Stage 4: + TPS62130 buck + J3 output header
Stage 5: full board (all nets routed)

Symbols are extracted verbatim from installed KiCad libraries (renamed to
lib-qualified form). Instances use real pin coordinates parsed from the
library unit blocks so wires land on actual pins.
"""
import os
import re
import sys
import uuid

OUT_SCH = "pcb/power-board/power-board.kicad_sch"
OUT_PRO = "pcb/power-board/power-board.kicad_pro"
SYM_LIB = "/usr/share/kicad/symbols"

PROJECT_UUID = "d1e2f3a4-5b6c-4d7e-8f90-a1b2c3d4e5f6"
SHEET_UUID = "e2f3a4b5-6c7d-4e8f-9a01-b2c3d4e5f607"


def gen_uuid(seed):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"power-board-{seed}"))


def extract_symbol(lib_text, name, lib_nick):
    marker = f'(symbol "{name}"'
    start = lib_text.find(marker)
    if start < 0:
        raise SystemExit(f"symbol {name} not found in {lib_nick}")
    depth = 0
    k = start
    instr = False
    while k < len(lib_text):
        ch = lib_text[k]
        if instr:
            if ch == '"':
                instr = False
        elif ch == '"':
            instr = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        k += 1
    block = lib_text[start:k + 1]
    block = block.replace(f'(symbol "{name}"', f'(symbol "{lib_nick}:{name}"', 1)
    return "\n".join("\t" + ln if ln.strip() else ln
                     for ln in block.split("\n"))


def pin_positions(block, name, unit=1):
    # merge the shared unit (_0_1) and the requested unit: pins common to
    # all units live in _0_1 in multi-unit symbols like DW01A
    pins = {}
    for suffix in ("_0_1", f"_{unit}_1"):
        i = block.find(f'(symbol "{name}{suffix}"')
        ubody = block[i:] if i >= 0 else block
        for m in re.finditer(
                r'\(pin \w+ \w+\s*\n\s*\(at (-?[\d.]+) (-?[\d.]+) (-?\d+)\)\s*\n'
                r'\s*\(length ([\d.]+)\)(?:(?!\(pin ).)*?\(number "([^"]+)"',
                ubody, re.S):
            x, y, _a, _l, num = m.groups()
            pins[num] = (float(x), float(y), float(_l), float(_a))
    return pins


def _old_pin_positions(block, name):
    i = block.find(f'(symbol "{name}_1_1"')
    unit = block[i:] if i >= 0 else block
    pins = {}
    for m in re.finditer(
            r'\(pin \w+ \w+\s*\n\s*\(at (-?[\d.]+) (-?[\d.]+) (-?\d+)\)\s*\n'
            r'\s*\(length ([\d.]+)\)(?:(?!\(pin ).)*?\(number "([^"]+)"',
            unit, re.S):
        x, y, _a, _l, num = m.groups()
        pins[num] = (float(x), float(y), float(_l), float(_a))
    return pins


LIBS = {
    "Connector": f"{SYM_LIB}/Connector.kicad_sym",
    "Battery_Management": f"{SYM_LIB}/Battery_Management.kicad_sym",
    "Regulator_Switching": f"{SYM_LIB}/Regulator_Switching.kicad_sym",
    "Device": f"{SYM_LIB}/Device.kicad_sym",
    "Transistor_FET": f"{SYM_LIB}/Transistor_FET.kicad_sym",
    "Connector_Generic": f"{SYM_LIB}/Connector_Generic.kicad_sym",
    "power": f"{SYM_LIB}/power.kicad_sym",
}


def load_all():
    texts = {k: open(v, encoding="utf-8").read() for k, v in LIBS.items()}
    return texts


class Schematic:
    def __init__(self):
        self.parts = []   # (kind, text)
        self.lib_symbols = {}

    def add_lib(self, nick, name, text):
        key = f"{nick}:{name}"
        if key not in self.lib_symbols:
            self.lib_symbols[key] = extract_symbol(text, name, nick)

    def instance(self, ref, value, footprint, x, y, nick, name, tag,
                 pin_override=None, unit=1):
        # snap symbol origin to the 1.27 mm schematic grid
        x = round(x / 1.27) * 1.27
        y = round(y / 1.27) * 1.27
        blk = extract_symbol(LIBS_TEXT[nick], name, nick)
        self.add_lib(nick, name, LIBS_TEXT[nick])
        pins = pin_positions(blk, name, unit=unit)
        parts = [
            "\t(symbol",
            f'\t\t(lib_id "{nick}:{name}")',
            f"\t\t(at {x:.2f} {y:.2f} 0)",
            f"\t\t(unit {unit})",
            "\t\t(exclude_from_sim no)",
            "\t\t(in_bom yes)",
            "\t\t(on_board yes)",
            "\t\t(dnp no)",
            f'\t\t(uuid "{gen_uuid("inst-" + tag)}")',
        ]
        for pname, val, dy, hidden in [
                ("Reference", ref, 4.0, False),
                ("Value", value, -4.0, False),
                ("Footprint", footprint, 0.0, True),
                ("Datasheet", "~", 0.0, True),
                ("Description", value, 0.0, True)]:
            parts.append(f'\t\t(property "{pname}" "{val}"')
            parts.append(f"\t\t\t(at {x:.2f} {y + dy:.2f} 0)")
            parts.append("\t\t\t(effects (font (size 1.27 1.27))" +
                         (" (hide yes))" if hidden else ")"))
            parts.append("\t\t)")
        for num in pins:
            parts.append(f'\t\t(pin "{num}"')
            parts.append(f'\t\t\t(uuid "{gen_uuid(f"{tag}-pin-{num}")}")')
            parts.append("\t\t)")
        parts.append("\t\t(instances")
        parts.append('\t\t\t(project "power-board"')
        parts.append(f'\t\t\t\t(path "/{PROJECT_UUID}"')
        parts.append(f'\t\t\t\t\t(reference "{ref}")')
        parts.append(f"\t\t\t\t\t(unit {unit})")
        parts.append("\t\t\t\t)")
        parts.append("\t\t\t)")
        parts.append("\t\t)")
        parts.append("\t)")
        self.parts.append("\n".join(parts))
        # absolute pin positions (symbol y axis is inverted on sheet).
        # In KiCad symbols, (at x y angle) of a pin IS the connection
        # point; length extends inward. So no length addition here.
        abs_pins = {num: (x + pdx, y - pdy, _l, _a)
                    for num, (pdx, pdy, _l, _a) in pins.items()}
        return abs_pins

    def wire(self, x1, y1, x2, y2, tag):
        self.parts.append(
            f'\t(wire\n\t\t(pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))\n'
            f'\t\t(stroke (width 0) (type default))\n'
            f'\t\t(uuid "{gen_uuid("wire-" + tag)}")\n\t)')

    def label(self, net, x, y, tag, angle=0):
        self.parts.append(
            f'\t(label "{net}"\n'
            f'\t\t(at {x:.2f} {y:.2f} {angle})\n'
            f'\t\t(effects (font (size 1.27 1.27)))\n'
            f'\t\t(uuid "{gen_uuid("lbl-" + tag)}")\n'
            f'\t)')

    def no_connect(self, x, y, tag):
        self.parts.append(
            f'\t(no_connect\n\t\t(at {x:.2f} {y:.2f})\n'
            f'\t\t(uuid "{gen_uuid("nc-" + tag)}")\n\t)')

    def pwr_flag(self, x, y, net, tag):
        # PWR_FLAG symbol from power lib: place and label the net
        self.add_lib("power", "PWR_FLAG", LIBS_TEXT["power"])
        self._flg_n = getattr(self, '_flg_n', 0) + 1
        flg_ref = f"#FLG{self._flg_n:02d}"
        self.parts.append(
            f'\t(symbol\n\t\t(lib_id "power:PWR_FLAG")\n'
            f'\t\t(at {x:.2f} {y:.2f} 0)\n\t\t(unit 1)\n'
            f'\t\t(exclude_from_sim no)\n\t\t(in_bom no)\n\t\t(on_board yes)\n'
            f'\t\t(dnp no)\n\t\t(uuid "{gen_uuid("pwrflag-" + tag)}")\n'
            f'\t\t(property "Reference" "#FLG"\n'
            f'\t\t\t(at {x:.2f} {y + 2.54:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n'
            f'\t\t(property "Value" "PWR_FLAG"\n'
            f'\t\t\t(at {x:.2f} {y - 2.54:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n'
            f'\t\t(property "Footprint" ""\n\t\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
            f'\t\t(property "Datasheet" "~"\n\t\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
            f'\t\t(property "Description" "Power flag"\n'
            f'\t\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
            f'\t\t(pin "1"\n\t\t\t(uuid "{gen_uuid("pf-pin-" + tag)}")\n\t\t)\n'
            f'\t\t(instances\n\t\t\t(project "power-board"\n'
            f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
            f'\t\t\t\t\t(reference "{flg_ref}")\n\t\t\t\t\t(unit 1)\n'
            f'\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')
        if net == "GND":
            # a plain local label named GND collides with the global
            # power:GND net name; use a power symbol offset below so the
            # two power pins do not stack on the same point
            gnd_at(x, y - 2.54, "pwr-" + tag)
            SCHEMATIC.wire(x, y, x, y - 2.54, "pwr-" + tag + "-w")
        else:
            self.label(net, x, y, "pwr-" + tag)

    def power_symbol(self, x, y, net, tag, num):
        """Place a power symbol (power:GND etc). The Value property IS the
        net name; a stub wire is not required when placed on a wire end."""
        blk = extract_symbol(LIBS_TEXT["power"], net, "power")
        self.add_lib("power", net, LIBS_TEXT["power"])
        pin = gen_uuid(f"ps-pin-{tag}-{num}")
        self.parts.append(
            f'\t(symbol\n\t\t(lib_id "power:{net}")\n'
            f'\t\t(at {x:.2f} {y:.2f} 0)\n\t\t(unit 1)\n'
            f'\t\t(exclude_from_sim no)\n\t\t(in_bom no)\n\t\t(on_board yes)\n'
            f'\t\t(dnp no)\n\t\t(uuid "{gen_uuid(f"ps-{tag}-{num}")}")\n'
            f'\t\t(property "Reference" "#PWR"\n'
            f'\t\t\t(at {x:.2f} {y + 6.35:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
            f'\t\t(property "Value" "{net}"\n'
            f'\t\t\t(at {x:.2f} {y + 3.81:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n'
            f'\t\t(property "Footprint" ""\n'
            f'\t\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
            f'\t\t(property "Datasheet" ""\n'
            f'\t\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
            f'\t\t(property "Description" "Power symbol creates a global label with name {net}"\n'
            f'\t\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
            f'\t\t(pin "1"\n\t\t\t(uuid "{pin}")\n\t\t)\n'
            f'\t\t(instances\n\t\t\t(project "power-board"\n'
            f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
            f'\t\t\t\t\t(reference "#PWR{num:02d}")\n'
            f'\t\t\t\t\t(unit 1)\n'
            f'\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')

    def render(self):
        libs = "\n".join(self.lib_symbols.values())
        body = "\n".join(p if isinstance(p, str) else p[1] for p in self.parts)
        return f'''(kicad_sch
\t(version 20241209)
\t(generator "gen_power_board")
\t(generator_version "9.0")
\t(uuid "{SHEET_UUID}")
\t(paper "A3")
\t(title_block
\t\t(title "PSP-3000 internal mod - power board")
\t\t(date "2026-10-13")
\t\t(rev "A")
\t\t(comment 1 "Stage-generated; validated with kicad-cli sch erc")
\t)
\t(lib_symbols

{libs}
\t)
{body}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)
'''


LIBS_TEXT = load_all()

SCHEMATIC = Schematic()
PWR_SYM_N = [0]  # running counter for #PWR references


def gnd_at(x, y, tag):
    """Attach a power:GND symbol at (x, y) with auto reference number."""
    PWR_SYM_N[0] += 1
    SCHEMATIC.power_symbol(x, y, "GND", tag, PWR_SYM_N[0])


def build_stage1():
    """USB-C receptacle, CC pulldowns, PWR_FLAG on VBUS."""
    pins = SCHEMATIC.instance(
        "J1", "USB_C_Receptacle_USB2.0_16P",
        "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
        120.0, 80.0, "Connector", "USB_C_Receptacle_USB2.0_16P", "J1")
    # library: A-side pins point left (-x), B-side right, S shields up
    # get concrete pin offsets from pin_positions: A1..A12 etc.
    # VBUS pins on the 16P symbol are A4, A9, B4, B9; GND A1,A12,B1,B12;
    # CC1 = A5, CC2 = B5; D+ = A6,B6; D- = A7,B7; SBU A8,B8; SHIELD S1,S2
    def p(num):
        return pins[num]

    # VBUS tie: A4 to a vertical bus
    vbus_x = p("A4")[0] - 3.81
    SCHEMATIC.wire(p("A4")[0], p("A4")[1], vbus_x, p("A4")[1], "vbus1")
    SCHEMATIC.wire(vbus_x, p("A4")[1], vbus_x, p("B4")[1], "vbus2")
    SCHEMATIC.wire(vbus_x, p("B4")[1], p("B4")[0], p("B4")[1], "vbus3")
    SCHEMATIC.label("VBUS", vbus_x, p("A4")[1], "vbus")
    # GND tie: A1,A12,B1,B12 down to a bus below the connector
    gy_raw = max(p(n)[1] for n in ("A1", "A12", "B1", "B12")) + 4.0
    gy = round(gy_raw / 1.27) * 1.27  # snap to schematic grid
    for num in ("A1", "A12", "B1", "B12"):
        px, py = p(num)[0], p(num)[1]
        SCHEMATIC.wire(px, py, px, gy, f"gnd-{num}")
    # bus spans from the leftmost to rightmost tied pin (incl. SH shield)
    xs = [p(n)[0] for n in ("A1", "A12", "B1", "B12")]
    if "SH" in pins:
        xs.append(pins["SH"][0])
    SCHEMATIC.wire(min(xs), gy, max(xs), gy, "gndbus")
    gnd_at(p("A1")[0], gy, "gnd")
    # CC1/CC2 pulldowns 5.1k: label at the pin end, Rd resistor hangs
    # from a label-joined stub (ERC-clean via matching net labels)
    for i, (num, net, ref) in enumerate((("A5", "CC1", "R1"),
                                         ("B5", "CC2", "R2"))):
        x, y = p(num)[0], p(num)[1]
        wx = x - 2.54
        SCHEMATIC.wire(x, y, wx, y, f"cc-{num}")
        SCHEMATIC.label(net, wx, y, f"lbl-{num}", angle=180)
        ry = y + 10.16 + i * 6.35
        rx = 155.0
        rpins = SCHEMATIC.instance(
            ref, "5.1k", "Resistor_SMD:R_0402_1005Metric",
            rx, ry, "Device", "R", ref)
        # R pin1 (top, sheet) to GND label; R pin2 to CCx label
        p1x, p1y, _l1, _a1 = rpins["1"]
        p2x, p2y, _l2, _a2 = rpins["2"]
        SCHEMATIC.wire(p1x, p1y, p1x, p1y - 2.54, f"{ref}-top")
        gnd_at(p1x, p1y - 2.54, f"{ref}-gnd")
        SCHEMATIC.wire(p2x, p2y, p2x, p2y + 2.54, f"{ref}-bot")
        SCHEMATIC.label(net, p2x, p2y + 2.54, f"{ref}-{net}")
    # PWR_FLAG on VBUS (flag pin connects to the VBUS wire)
    SCHEMATIC.pwr_flag(vbus_x - 5.08, p("A4")[1], "VBUS", "vbus")
    # shield pins to GND (this symbol exposes a single SH pin pair)
    for num in ("S1", "S2", "SH"):
        if num in pins:
            x, y = p(num)[0], p(num)[1]
            SCHEMATIC.wire(x, y, x, gy, f"sh-{num}")
    # if SH exists but is above the bus, extend its wire to the bus line
    if "SH" in pins:
        x, y, _ls, _as = pins["SH"]
        SCHEMATIC.wire(x, gy, x, gy, "sh-extra")
    # USB2.0 data + SBU pins are unused on this board: explicit no-connect
    for num in ("A6", "A7", "B6", "B7", "A8", "B8"):
        if num in pins:
            SCHEMATIC.no_connect(pins[num][0], pins[num][1], f"nc-{num}")


def build_stage2():
    """BQ25895 charger core."""
    pins = SCHEMATIC.instance(
        "U1", "BQ25895RTW",
        "Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm",
        200.0, 80.0, "Battery_Management", "BQ25895RTW", "U1")
    # Label each pin through a short stub wire (a label directly on a
    # pin is reported as isolated_pin_label by KiCad 10 ERC).
    netmap = {
        "1": "VBUS",       # VBUS
        "4": "STAT", "5": "SCL", "6": "SDA", "7": "INT",
        "8": "OTG", "9": "CE",
        "10": "ILIM",
        "11": "TS",
        "12": "BAT", "13": "BAT", "14": "BAT",
        "15": "SYS", "16": "SYS",
        "17": "GND", "18": "GND",
        "19": "SW", "20": "SW", "21": "BTST", "22": "REGN",
        "23": "PMID",
    }
    for num, net in netmap.items():
        _pin_stub(pins, num, net, "u1", _pin_side(pins, num, 199.39))
    # USB data pins unused: charging-only design, BC1.2 detection off
    # (DSEL low below), so D+/D- are explicitly unconnected
    for num in ("2", "3", "24"):
        if num in pins:
            SCHEMATIC.no_connect(pins[num][0], pins[num][1], f"u1-nc{num}")
    # exposed pad (25) = PGND tie
    if "25" in pins:
        x, y, _l25, _a25 = pins["25"]
        gnd_at(x, y + 2.54, "u1-ep")
        SCHEMATIC.wire(x, y, x, y + 2.54, "u1-ep-stub")


def _pin_stub(pins, num, net, tag, side, jog=0.0):
    """Wire a short stub from pin `num` and put `net` label on its end.
    GND nets get a power:GND symbol instead of a plain label.
    `jog` shifts the stub end vertically to separate co-located pins
    (some library symbols stack same-potential pins on one point)."""
    if num not in pins:
        return
    x, y, _ln, _an = pins[num]
    dx, dy = side
    # vertical jog first so co-located pins leave the shared point apart
    if jog:
        SCHEMATIC.wire(x, y, x, y + jog, f"{tag}-{num}-jog")
        x, y = x, y + jog
    wx, wy = x + dx, y + dy
    SCHEMATIC.wire(x, y, wx, wy, f"{tag}-{num}-stub")
    if net == "GND":
        gnd_at(wx, wy, f"{tag}-{num}")
    else:
        SCHEMATIC.label(net, wx, wy, f"{tag}-{num}")


LEFT = (-2.54, 0.0)
RIGHT = (2.54, 0.0)
DOWN = (0.0, 2.54)
UP = (0.0, -2.54)


def _pin_side(pins, num, cx):
    """Stub direction from the pin's own angle: the (at) of a pin points
    outward, so extend the stub along the pin angle."""
    import math
    _x, _y, _l, ang = pins[num]
    # KiCad lib angle convention (y-down): 0=left, 90=down, 180=right,
    # 270=up. Sheet y grows downward too, so the direction maps over
    # unchanged: dx = -cos(ang), dy = +sin(ang).
    rad = math.radians(ang)
    dx = -math.cos(rad)
    dy = math.sin(rad)
    return (round(dx, 2) * 2.54, round(dy, 2) * 2.54)


def build_stage3():
    """DW01A + Q1 protection + J2 battery connector.

    Nets (DW01A datasheet, SparkFun DW01-P V10 copy in docs/evidence/):
    BAT+ -> J2.1, pack positive sense; DW01 VCC; Q1 sources common.
    BAT- -> J2.2 -> DW01 GND.
    DW01 OD -> Q1 gate 1, DW01 OC -> Q1 gate 2 (dual NMOS discharge/
    charge FETs in the pack negative path).
    """
    u2 = SCHEMATIC.instance(
        "U2", "DW01A", "Package_TO_SOT_SMD:SOT-23-6",
        220.0, 110.0, "Battery_Management", "DW01A", "U2")
    # Dual NMOS = 2 units: unit 1 = discharge FET (pins 1 D1, 5 G1, 6 S1),
    # unit 2 = charge FET (pins 2 D2, 3 G2, 4 S2). Place both units.
    q1a = SCHEMATIC.instance(
        "Q1", "Q_Dual_NMOS_G1S2G2D2S1D1",
        "Package_TO_SOT_SMD:SOT-23-6",
        252.0, 108.0, "Transistor_FET", "Q_Dual_NMOS_G1S2G2D2S1D1", "Q1A",
        unit=1)
    q1b = SCHEMATIC.instance(
        "Q1", "Q_Dual_NMOS_G1S2G2D2S1D1",
        "Package_TO_SOT_SMD:SOT-23-6",
        252.0, 118.0, "Transistor_FET", "Q_Dual_NMOS_G1S2G2D2S1D1", "Q1B",
        unit=2)
    q1 = q1a
    j2 = SCHEMATIC.instance(
        "J2", "Battery", "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal",
        175.0, 115.0, "Connector_Generic", "Conn_01x02", "J2")
    u2c = 220.0
    q1c = 252.0
    j2c = 175.0
    # battery connector: pin1 = BAT+ (pack positive), pin2 = BAT- (pack neg)
    _pin_stub(j2, "1", "BAT", "j2", RIGHT)
    _pin_stub(j2, "2", "PACKNEG", "j2", RIGHT)
    # DW01A: VCC (pin? per DW01A SOT-23-6: 1=OD 2=CS 3=OC 4=TD 5=NC 6=VCC
    # per SparkFun DW01-P: 1 OD, 2 CS (current sense / GND), 3 OC, 4 TD
    # (test), 5 NC, 6 VCC. GND is pin 2 (CS is the GND/current sense).
    # DW01A pinout (SOT-23-6, SparkFun DW01-P datasheet copy):
    # 1 OD (discharge FET gate), 2 CS/GND, 3 OC (charge FET gate),
    # 4 TD (test, leave open), 5 NC, 6 VCC
    dw_netmap = {"1": "PROT_OD", "2": "BATGND", "3": "PROT_OC",
                 "6": "BAT"}
    for num, net in dw_netmap.items():
        _pin_stub(u2, num, net, "u2", _pin_side(u2, num, u2c))
    for num in ("4", "5"):
        if num in u2:
            SCHEMATIC.no_connect(u2[num][0], u2[num][1], f"u2-nc{num}")
    # Q1 dual NMOS: G1 S2 G2 D2 S1 D1 per symbol name.
    # Discharge FET: D1 = BAT-, S1 = pack negative node (BATGND).
    # Charge FET:    D2 = pack negative node, S2 = system ground return.
    # DW01A + dual-FET standard topology (datasheet): pack negative B-
    # enters FET1 drain, FET1 source ties FET2 drain, FET2 source is the
    # system ground return. OD gates FET1 (discharge), OC gates FET2
    # (charge). unit 1 = pins 1(D1) 5(G1) 6(S1), unit 2 = 2(D2) 3(G2) 4(S2).
    for num, net in (("1", "PROT_OD"), ("6", "PACKNEG"), ("5", "FETMID")):
        _pin_stub(q1a, num, net, "q1a", _pin_side(q1a, num, q1c))
    for num, net in (("3", "PROT_OC"), ("4", "FETMID"), ("2", "BATGND")):
        _pin_stub(q1b, num, net, "q1b", _pin_side(q1b, num, q1c))


def build_stage4():
    """TPS62130 buck + J3 output header."""
    u3 = SCHEMATIC.instance(
        "U3", "TPS62130",
        "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm",
        265.0, 80.0, "Regulator_Switching", "TPS62130", "U3")
    j3 = SCHEMATIC.instance(
        "J3", "PWR_OUT", "Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical",
        310.0, 100.0, "Connector_Generic", "Conn_02x05_Odd_Even", "J3")
    # TPS62130 pinout per the KiCad library symbol (matches TI datasheet):
    # 1,2,3 SW / 4 PG / 5 FB / 6,15,16,17 GND / 7 FSW / 8 DEF / 9 SS/TR
    # 10,11,12 VIN / 13 EN / 14 VOS. Same-potential pins share coordinates.
    u3c = 265.0
    u3_nets = {
        "1": "SW33", "2": "SW33", "3": "SW33", "4": "PG33",
        "5": "VOS33", "6": "GND", "7": "GND", "8": "GND",
        "9": "GND", "10": "BAT", "11": "BAT", "12": "BAT",
        "13": "EN33", "14": "VOS33", "15": "GND", "16": "GND",
    }
    # Co-located pins share one sheet point; give the group members
    # vertical jogs so their stubs leave the shared point separately.
    u3_jogs = {"1": -2.54, "2": 0.0, "3": 2.54,
               "10": -2.54, "11": 0.0, "12": 2.54,
               "6": 2.54, "15": 0.0, "16": -2.54}
    for num, net in u3_nets.items():
        side = _pin_side(u3, num, u3c)
        _pin_stub(u3, num, net, "u3", side, jog=u3_jogs.get(num, 0.0))
    # NOTE: pin 17 here is a GND passive on the bottom edge (handled in
    # the loop above); the footprint's exposed pad ties to the same net.
    # J3: 5V rail to SBC + GND (2x05 header, 5V on pin 2/4 per Radxa GPIO)
    j3c = 310.0
    j3_nets = {"1": "VBUS", "2": "VBUS", "3": "GND", "4": "GND",
               "5": "BAT", "6": "GND", "7": "EN33", "8": "GND",
               "9": "STAT", "10": "GND"}
    for num, net in j3_nets.items():
        _pin_stub(j3, num, net, "j3", _pin_side(j3, num, j3c))


def build_stage5():
    """Interconnect passives: input/output caps, ILIM resistor, inductor."""
    # L1 (buck inductor): SW33 -> VOS33
    l1 = SCHEMATIC.instance(
        "L1", "2.2uH", "Inductor_SMD:L_0805_2012Metric",
        295.0, 70.0, "Device", "L", "L1")
    _pin_stub(l1, "1", "SW33", "l1", _pin_side(l1, "1", 295.0))
    _pin_stub(l1, "2", "VOS33", "l1", _pin_side(l1, "2", 295.0))
    # R3 ILIM: VBUS -> ILIM (KILIM 390 typ, 2A -> 195 ohm -> E96 196R)
    r3 = SCHEMATIC.instance(
        "R3", "196R", "Resistor_SMD:R_0402_1005Metric",
        155.0, 40.0, "Device", "R", "R3")
    _pin_stub(r3, "1", "VBUS", "r3", _pin_side(r3, "1", 155.0))
    _pin_stub(r3, "2", "ILIM", "r3", _pin_side(r3, "2", 155.0))
    # R4 OTG pulldown: OTG -> GND (OTG disabled by default)
    r4 = SCHEMATIC.instance(
        "R4", "100k", "Resistor_SMD:R_0402_1005Metric",
        165.0, 40.0, "Device", "R", "R4")
    _pin_stub(r4, "1", "OTG", "r4", _pin_side(r4, "1", 165.0))
    _pin_stub(r4, "2", "GND", "r4", _pin_side(r4, "2", 165.0))
    # R5 CE pullup: CE -> REGN (charging enabled by default)
    r5 = SCHEMATIC.instance(
        "R5", "100k", "Resistor_SMD:R_0402_1005Metric",
        175.0, 40.0, "Device", "R", "R5")
    _pin_stub(r5, "1", "CE", "r5", _pin_side(r5, "1", 175.0))
    _pin_stub(r5, "2", "REGN", "r5", _pin_side(r5, "2", 175.0))
    # R6/R7/R9: I2C + INT pullups to REGN.  R8 (STAT) is intentionally
    # absent: STAT is open-drain and its pull-up lives on the Radxa side
    # (3.3 V) - see docs/harness-j3-radxa.md and UNKNOWNS U11.  Pulling
    # STAT to REGN (4.7 V) would over-stress the SBC GPIO.
    for ref, net, x in (("R6", "SCL", 165.0), ("R7", "SDA", 175.0),
                        ("R9", "INT", 195.0)):
        r = SCHEMATIC.instance(
            ref, "10k", "Resistor_SMD:R_0402_1005Metric",
            x, 30.0, "Device", "R", ref)
        _pin_stub(r, "1", net, ref.lower(), _pin_side(r, "1", x))
        _pin_stub(r, "2", "REGN", ref.lower(), _pin_side(r, "2", x))
    # C1 PMID bypass 8.2uF (datasheet no-OTG value), PMID -> GND
    c1 = SCHEMATIC.instance(
        "C1", "8.2uF", "Capacitor_SMD:C_0805_2012Metric",
        205.0, 40.0, "Device", "C", "C1")
    _pin_stub(c1, "1", "PMID", "c1", _pin_side(c1, "1", 205.0))
    _pin_stub(c1, "2", "GND", "c1", _pin_side(c1, "2", 205.0))
    # C2 bootstrap cap 0.047uF BTST -> SW (datasheet)
    c2 = SCHEMATIC.instance(
        "C2", "47nF", "Capacitor_SMD:C_0402_1005Metric",
        215.0, 40.0, "Device", "C", "C2")
    _pin_stub(c2, "1", "BTST", "c2", _pin_side(c2, "1", 215.0))
    _pin_stub(c2, "2", "SW", "c2", _pin_side(c2, "2", 215.0))
    # TS divider: R10 REGN->TS, R11 TS->GND (103AT-2 style mid-scale,
    # enables charging without an NTC for bench bring-up; the donor
    # pack NTC replaces R11 at integration time)
    r10 = SCHEMATIC.instance(
        "R10", "10k", "Resistor_SMD:R_0402_1005Metric",
        225.0, 40.0, "Device", "R", "R10")
    _pin_stub(r10, "1", "REGN", "r10", _pin_side(r10, "1", 225.0))
    _pin_stub(r10, "2", "TS", "r10", _pin_side(r10, "2", 225.0))
    r11 = SCHEMATIC.instance(
        "R11", "10k", "Resistor_SMD:R_0402_1005Metric",
        235.0, 40.0, "Device", "R", "R11")
    _pin_stub(r11, "1", "TS", "r11", _pin_side(r11, "1", 235.0))
    _pin_stub(r11, "2", "GND", "r11", _pin_side(r11, "2", 235.0))
    # R12 PG33 pullup to VOS33 (open-drain power-good)
    r12 = SCHEMATIC.instance(
        "R12", "10k", "Resistor_SMD:R_0402_1005Metric",
        245.0, 40.0, "Device", "R", "R12")
    _pin_stub(r12, "1", "PG33", "r12", _pin_side(r12, "1", 245.0))
    _pin_stub(r12, "2", "VOS33", "r12", _pin_side(r12, "2", 245.0))
    # power flags so ERC sees GND and BAT as driven sources
    SCHEMATIC.pwr_flag(139.7, 129.54, "GND", "gnd")
    SCHEMATIC.pwr_flag(149.86, 129.54, "BAT", "bat")


def render(stage):
    sch = SCHEMATIC.render()
    with open(OUT_SCH, "w", encoding="utf-8") as fh:
        fh.write(sch)
    pro = f'''{{
  "board": {{}},
  "meta": {{"filename": "power-board.kicad_pro", "version": 3}},
  "net_settings": {{"classes": [{{"name": "Default", "clearance": 0.13,
      "track_width": 0.2, "via_diameter": 0.4, "via_drill": 0.2}}],
    "meta": {{"version": 4}}}},
  "boards": [],
  "cvpcb": {{"equivalence_files": []}},
  "libraries": {{"pinned_footprint_libs": [], "pinned_symbol_libs": []}},
  "pcbnew": {{"last_paths": {{}}, "page_layout_descr_file": ""}},
  "schematic": {{"legacy_lib_dir": "", "legacy_lib_list": [],
    "meta": {{"version": 1}}, "page_layout_descr_file": "",
    "plot_directory": ""}},
  "sheets": [["{SHEET_UUID}", "Root"]],
  "text_variables": {{}}
}}'''
    with open(OUT_PRO, "w", encoding="utf-8") as fh:
        fh.write(pro)
    print(f"stage {stage}: wrote {OUT_SCH}")


def main():
    stage = int(sys.argv[sys.argv.index("--stage") + 1]) \
        if "--stage" in sys.argv else 1
    os.makedirs("pcb/power-board", exist_ok=True)
    build_stage1()
    if stage >= 2:
        build_stage2()
    if stage >= 3:
        build_stage3()
    if stage >= 4:
        build_stage4()
    if stage >= 5:
        build_stage5()
    render(stage)


if __name__ == "__main__":
    main()
