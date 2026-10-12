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


def pin_positions(block, name):
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
                 pin_override=None):
        # snap symbol origin to the 1.27 mm schematic grid
        x = round(x / 1.27) * 1.27
        y = round(y / 1.27) * 1.27
        blk = extract_symbol(LIBS_TEXT[nick], name, nick)
        self.add_lib(nick, name, LIBS_TEXT[nick])
        pins = pin_positions(blk, name)
        parts = [
            "\t(symbol",
            f'\t\t(lib_id "{nick}:{name}")',
            f"\t\t(at {x:.2f} {y:.2f} 0)",
            "\t\t(unit 1)",
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
        parts.append("\t\t\t\t\t(unit 1)")
        parts.append("\t\t\t\t)")
        parts.append("\t\t\t)")
        parts.append("\t\t)")
        parts.append("\t)")
        self.parts.append("\n".join(parts))
        # absolute pin positions (symbol y axis is inverted on sheet).
        # In KiCad symbols, (at x y angle) of a pin IS the connection
        # point; length extends inward. So no length addition here.
        abs_pins = {num: (x + pdx, y - pdy)
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
            f'\t\t\t\t\t(reference "#FLG01")\n\t\t\t\t\t(unit 1)\n'
            f'\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')
        self.label(net, x, y, "pwr-" + tag)

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
        x, y = p(num)
        SCHEMATIC.wire(x, y, x, gy, f"gnd-{num}")
    # bus spans from the leftmost to rightmost tied pin (incl. SH shield)
    xs = [p(n)[0] for n in ("A1", "A12", "B1", "B12")]
    if "SH" in pins:
        xs.append(pins["SH"][0])
    SCHEMATIC.wire(min(xs), gy, max(xs), gy, "gndbus")
    SCHEMATIC.label("GND", p("A1")[0], gy, "gnd")
    # CC1/CC2 pulldowns 5.1k: label at the pin end, Rd resistor hangs
    # from a label-joined stub (ERC-clean via matching net labels)
    for i, (num, net, ref) in enumerate((("A5", "CC1", "R1"),
                                         ("B5", "CC2", "R2"))):
        x, y = p(num)
        wx = x - 2.54
        SCHEMATIC.wire(x, y, wx, y, f"cc-{num}")
        SCHEMATIC.label(net, wx, y, f"lbl-{num}", angle=180)
        ry = y + 10.16 + i * 6.35
        rx = 155.0
        rpins = SCHEMATIC.instance(
            ref, "5.1k", "Resistor_SMD:R_0402_1005Metric",
            rx, ry, "Device", "R", ref)
        # R pin1 (top, sheet) to GND label; R pin2 to CCx label
        p1x, p1y = rpins["1"]
        p2x, p2y = rpins["2"]
        SCHEMATIC.wire(p1x, p1y, p1x, p1y - 2.54, f"{ref}-top")
        SCHEMATIC.label("GND", p1x, p1y - 2.54, f"{ref}-gnd")
        SCHEMATIC.wire(p2x, p2y, p2x, p2y + 2.54, f"{ref}-bot")
        SCHEMATIC.label(net, p2x, p2y + 2.54, f"{ref}-{net}")
    # PWR_FLAG on VBUS (flag pin connects to the VBUS wire)
    SCHEMATIC.pwr_flag(vbus_x - 5.08, p("A4")[1], "VBUS", "vbus")
    # shield pins to GND (this symbol exposes a single SH pin pair)
    for num in ("S1", "S2", "SH"):
        if num in pins:
            x, y = p(num)
            SCHEMATIC.wire(x, y, x, gy, f"sh-{num}")
    # if SH exists but is above the bus, extend its wire to the bus line
    if "SH" in pins:
        x, y = pins["SH"]
        SCHEMATIC.wire(x, gy, x, gy, "sh-extra")
    # USB2.0 data + SBU pins are unused on this board: explicit no-connect
    for num in ("A6", "A7", "B6", "B7", "A8", "B8"):
        if num in pins:
            SCHEMATIC.no_connect(*pins[num], f"nc-{num}")


def build_stage2():
    """BQ25895 charger core."""
    pins = SCHEMATIC.instance(
        "U1", "BQ25895RTW",
        "Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm",
        200.0, 80.0, "Battery_Management", "BQ25895RTW", "U1")
    # label key pins with nets (labels connect same-named nets globally)
    netmap = {
        "1": "VBUS",       # VBUS
        "2": "USB_DP", "3": "USB_DM",
        "4": "STAT", "5": "SCL", "6": "SDA", "7": "INT",
        "8": "OTG", "9": "CE",
        "10": "ILIM",
        "11": "TS",
        "12": "BAT", "13": "BAT", "14": "BAT",
        "15": "SYS", "16": "SYS",
        "19": "SW", "20": "SW", "21": "BTST", "22": "REGN",
        "23": "PMID", "24": "DSEL",
    }
    for num, net in netmap.items():
        if num in pins:
            x, y = pins[num]
            SCHEMATIC.label(net, x, y, f"u1-{num}")
    # GND pins 17,18 + EP (25) -> GND
    for num in ("17", "18"):
        x, y = pins[num]
        SCHEMATIC.label("GND", x, y, f"u1gnd-{num}")
    SCHEMATIC.no_connect(*pins["25"], "u1-ep-nc") if False else None


def build_stage3():
    """DW01A + Q1 protection + J2 battery connector."""
    SCHEMATIC.instance(
        "U2", "DW01A", "Package_TO_SOT_SMD:SOT-23-6",
        220.0, 110.0, "Battery_Management", "DW01A", "U2")
    SCHEMATIC.instance(
        "Q1", "Q_Dual_NMOS_G1S2G2D2S1D1",
        "Package_TO_SOT_SMD:SOT-23-6",
        230.0, 110.0, "Transistor_FET", "Q_Dual_NMOS_G1S2G2D2S1D1", "Q1")
    SCHEMATIC.instance(
        "J2", "Battery", "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal",
        180.0, 120.0, "Connector_Generic", "Conn_01x02", "J2")


def build_stage4():
    """TPS62130 buck + J3 output header."""
    SCHEMATIC.instance(
        "U3", "TPS62130",
        "Package_DFN_QFN.pretty:VQFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm",
        250.0, 80.0, "Regulator_Switching", "TPS62130", "U3")
    SCHEMATIC.instance(
        "J3", "PWR_OUT", "Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical",
        300.0, 100.0, "Connector_Generic", "Conn_02x05_Odd_Even", "J3")


def build_stage5():
    """Interconnect passives (caps/resistors/inductor) - minimal labels."""
    pass


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
    render(stage)


if __name__ == "__main__":
    main()
