#!/usr/bin/env python3
"""Generate a KiCad 10 project: SVDI capture breakout board (v2).

Board function: 31-pin 0.5mm-pitch FPC connector (panel pin map per
docs/evidence/lcd-LQ043T3LX02.md Table 6-3) breaking out to a 2x20 1.27mm
capture header for logic-analyzer work. Symbol definitions are extracted
verbatim from the installed KiCad standard library
(/usr/share/kicad/symbols/Connector_Generic.kicad_sym) - no hand-authored
symbol syntax.

Usage: python3 scripts/gen_svdi_breakout.py   (from repo root)
"""
import os
import uuid

OUT_SCH = "pcb/svdi-breakout/svdi-breakout.kicad_sch"
OUT_PRO = "pcb/svdi-breakout/svdi-breakout.kicad_pro"
LIB_PATH = "/usr/share/kicad/symbols/Connector_Generic.kicad_sym"

PROJECT_UUID = "b7e3a1c2-5d4e-4f6a-9b8c-1a2b3c4d5e6f"
SHEET_UUID = "c8f4b2d3-6e5f-4a7b-ac9d-2b3c4d5e6f70"


def gen_uuid(seed):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"svdi-breakout-{seed}"))


def extract_symbol(lib_text, name, lib_nick):
    """Extract (symbol "NAME" ...) from a .kicad_sym, renaming to
    lib-qualified "NICK:NAME" as required inside kicad_sch lib_symbols."""
    marker = f'(symbol "{name}"'
    start = lib_text.find(marker)
    if start < 0:
        raise SystemExit(f"symbol {name} not found in {LIB_PATH}")
    header_old = f'(symbol "{name}"'
    header_new = f'(symbol "{lib_nick}:{name}"'
    # rename only the header occurrence (first line of the block)
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
    block = block.replace(header_old, header_new, 1)
    # re-indent: lib file uses 1 tab at top level; embedded needs 2
    lines = block.split("\n")
    out = []
    for ln in lines:
        out.append("\t" + ln if ln.strip() else ln)
    return "\n".join(out)


def sch_instance(ref, value, footprint, x, y, lib_value, npins, tag):
    """Returns (symbol_block, extra_items) - extra = top-level no_connects."""
    """One placed symbol. lib_id points at the embedded lib symbol."""
    props = [
        ("Reference", ref, 3.81),
        ("Value", value, -3.81),
        ("Footprint", footprint, None),
        ("Datasheet", "~", None),
        ("Description", value, None),
    ]
    parts = [
        "\t(symbol",
        f'\t\t(lib_id "Connector_Generic:{lib_value}")',
        f"\t\t(at {x:.2f} {y:.2f} 0)",
        "\t\t(unit 1)",
        "\t\t(exclude_from_sim no)",
        "\t\t(in_bom yes)",
        "\t\t(on_board yes)",
        "\t\t(dnp no)",
        f'\t\t(uuid "{gen_uuid("inst-" + tag)}")',
    ]
    for name, val, dy in props:
        hidden = dy is None
        at = (f"{x:.2f} {y + dy:.2f}" if not hidden else f"{x:.2f} {y:.2f}")
        if hidden:
            parts.append(f'\t\t(property "{name}" "{val}"')
            parts.append(f"\t\t\t(at {at} 0)")
            parts.append("\t\t\t(effects (font (size 1.27 1.27)) (hide yes))")
            parts.append("\t\t)")
        else:
            parts.append(f'\t\t(property "{name}" "{val}"')
            parts.append(f"\t\t\t(at {at} 0)")
            parts.append("\t\t\t(effects (font (size 1.27 1.27)))")
            parts.append("\t\t)")
    # pin uuids
    for n in range(1, npins + 1):
        parts.append(f'\t\t(pin "{n}"')
        parts.append(f'\t\t\t(uuid "{gen_uuid(f"{tag}-pin-{n}")}")')
        parts.append("\t\t)")
    parts.append("\t\t(instances")
    parts.append('\t\t\t(project "svdi-breakout"')
    parts.append(f'\t\t\t\t(path "/{PROJECT_UUID}"')
    parts.append(f'\t\t\t\t\t(reference "{ref}")')
    parts.append("\t\t\t\t\t(unit 1)")
    parts.append("\t\t\t\t)")
    parts.append("\t\t\t)")
    parts.append("\t\t)")
    parts.append("\t)")
    extras = ""
    if tag == "J2":
        extras = "\n".join(
            f'\t(no_connect\n\t\t(at {x - 5.08:.2f} '
            f'{27.94 + (n - 1) * 2.54:.2f})\n'
            f'\t\t(uuid "{gen_uuid(f"{tag}-nc-{n}")}")\n'
            f'\t)' for n in range(32, 41)) + "\n"
    return "\n".join(parts) + "\n", extras


def main():
    os.makedirs("pcb/svdi-breakout", exist_ok=True)
    with open(LIB_PATH, encoding="utf-8") as fh:
        lib_text = fh.read()

    sym31 = extract_symbol(lib_text, "Conn_01x31", "Connector_Generic")
    sym40 = extract_symbol(lib_text, "Conn_01x40", "Connector_Generic")

    j1, _ = sch_instance(
        "J1", "FPC31",
        "Connector_FFC-FPC:Amphenol_F32Q-1A7x1-11031_1x31-1MP_P0.5mm_Horizontal",
        127.0, 76.2, "Conn_01x31", 31, "J1")
    j2, j2_nc = sch_instance(
        "J2", "HDR40",
        "Connector_PinHeader_1.27mm:PinHeader_1x40_P1.27mm_Vertical",
        190.5, 76.2, "Conn_01x40", 40, "J2")

    # Local labels + short wires: FPC pin stubs (left) and header pin stubs
    # (right). Same local net name on both sides connects them for
    # netlisting; wires satisfy the connection rule.
    pinmap = [
        (1, "COM"), (2, "PNL"), (3, "NC"), (4, "VGL"), (5, "NC"),
        (6, "VGH"), (7, "VL"), (8, "VH"), (9, "GND"), (10, "VS"),
        (11, "VS"), (12, "GND"), (13, "VCC"), (14, "SDO"), (15, "SDI"),
        (16, "SCLK"), (17, "SCS"), (18, "REV"), (19, "RESETB"),
        (20, "GNDRX"), (21, "DATA2P"), (22, "DATA2N"), (23, "GNDRX"),
        (24, "CLKP"), (25, "CLKN"), (26, "GNDRX"), (27, "DATA1P"),
        (28, "DATA1N"), (29, "GNDRX"), (30, "VCCRX"), (31, "COM"),
    ]
    wires = []
    labels = []
    # FPC Conn_01x31 pin n: screen y = 38.1 + (n-1)*2.54 (pin 1 at top;
    # KiCad sch Y grows downward). Pin exits at x = 127 - 5.08.
    for n, net in pinmap:
        y = 38.1 + (n - 1) * 2.54
        x_pin = 127.0 - 5.08
        x_end = x_pin - 2.54
        wires.append(f'\t(wire\n\t\t(pts (xy {x_end:.2f} {y:.2f}) '
                     f'(xy {x_pin:.2f} {y:.2f}))\n'
                     f'\t\t(stroke (width 0) (type default))\n'
                     f'\t\t(uuid "{gen_uuid(f"wire-fpc-{n}")}")\n\t)')
        labels.append(
            f'\t(label "{net}"\n'
            f'\t\t(at {x_end:.2f} {y:.2f} 0)\n'
            f'\t\t(effects (font (size 1.27 1.27)))\n'
            f'\t\t(uuid "{gen_uuid(f"lbl-fpc-{n}")}")\n'
            f'\t)')
    # header pin n: screen y = 27.94 + (n-1)*2.54 (pin 1 top, Y grows down);
    # pins 32..40 get no_connect flags (top-level items from sch_instance)
    for n in range(1, 32):
        net = pinmap[n - 1][1]
        y = 27.94 + (n - 1) * 2.54
        x_pin = 190.5 - 5.08
        x_end = x_pin + 2.54
        wires.append(f'\t(wire\n\t\t(pts (xy {x_pin:.2f} {y:.2f}) '
                     f'(xy {x_end:.2f} {y:.2f}))\n'
                     f'\t\t(stroke (width 0) (type default))\n'
                     f'\t\t(uuid "{gen_uuid(f"wire-hdr-{n}")}")\n\t)')
        labels.append(
            f'\t(label "{net}"\n'
            f'\t\t(at {x_end:.2f} {y:.2f} 0)\n'
            f'\t\t(effects (font (size 1.27 1.27)))\n'
            f'\t\t(uuid "{gen_uuid(f"lbl-hdr-{n}")}")\n'
            f'\t)')
    wires_s = "\n".join(wires)
    labels_s = "\n".join(labels)

    sch = f'''(kicad_sch
\t(version 20241209)
\t(generator "opencbm")
\t(generator_version "9.0")
\t(uuid "{SHEET_UUID}")
\t(paper "A4")
\t(title_block
\t\t(title "PSP-3000 SVDI capture breakout")
\t\t(date "2026-10-13")
\t\t(rev "A")
\t\t(comment 1 "Panel pin map per Sharp LCM-09006 Table 6-3 (VPS)")
\t\t(comment 2 "31-pin 0.5mm FPC -> 40-pin 1.27mm capture header")
\t)
\t(lib_symbols
{sym31}
{sym40}
\t)
{j1}{j2}
{j2_nc}
{wires_s}
{labels_s}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
'''
    with open(OUT_SCH, "w", encoding="utf-8") as fh:
        fh.write(sch)

    pro = '''{
  "board": {
    "3dviewports": [],
    "ipc2581": {"dist": "", "distpn": "", "internal_id": "", "mfg": "", "mpn": ""},
    "layer_pairs": [], "layer_presets": [], "viewports": []
  },
  "boards": [],
  "cvpcb": {"equivalence_files": []},
  "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
  "meta": {"filename": "svdi-breakout.kicad_pro", "version": 3},
  "net_settings": {"classes": [
      {"bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25,
       "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
       "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1,
       "name": "Default", "pcb_color": "rgba(0, 0, 0, 0.000)",
       "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": 0.2,
       "via_diameter": 0.6, "via_drill": 0.3, "wire_width": 6}
    ],
    "meta": {"version": 4}, "net_colors": null},
  "pcbnew": {"last_paths": {"gencad": "", "dxf": "", "file": "", "idf": "",
      "netlist": "", "plot": "", "pos_files": "", "specctra_dsn": "",
      "step": "", "svg": "", "vrml": ""},
    "page_layout_descr_file": ""},
  "schematic": {"annotate_start_num": 0, "bom_export_filename": "",
    "bom_fmt_presets": [], "bom_fmt_settings": {},
    "bom_presets": [], "bom_settings": {},
    "connection_grid_size": 50.0,
    "drawing": {"default_line_thickness": 6.0,
      "default_text_size": 50.0, "label_size_ratio": 0.375,
      "pin_symbol_size": 25.0, "text_offset_ratio": 0.15},
    "legacy_lib_dir": "", "legacy_lib_list": [],
    "meta": {"version": 1},
    "net_format_name": "",
    "page_layout_descr_file": "",
    "plot_directory": "",
    "spice_current_sheet_as_root": false,
    "spice_external_command": "spice \\"%I\\"",
    "spice_model_current_sheet_as_root": true,
    "spice_save_all_currents": false,
    "subpart_first_id": 65, "subpart_id_separator": 0},
  "sheets": [[f"{SHEET_UUID}", "Root"]],
  "text_variables": {}
}
'''.replace('f"{SHEET_UUID}"', f'"{SHEET_UUID}"')
    with open(OUT_PRO, "w", encoding="utf-8") as fh:
        fh.write(pro)
    print(f"wrote {OUT_SCH} and {OUT_PRO}")


if __name__ == "__main__":
    main()
