#!/usr/bin/env python3
"""Generate the power board PCB from the completed schematic (Phase 6).

Approach mirrors scripts/gen_svdi_breakout_pcb.py:
- netlist (pcb/power-board/power-board.net) is the source of truth
- footprints loaded from the KiCad stock library
- placement: rows keyed by reference (J1 USB-C edge, ICs center,
  passives grouped near their IC, J2/J3 at board edges)
- routing: layer-separation switchbox (F.Cu horizontal, B.Cu vertical)
- board outline derived from mechanical envelope in cad/params.md

Constraints are written into power-board.kicad_pro
board.design_settings.rules (KiCad 10 reads them from there only).
"""
import os
import re
import sys

sys.path.insert(0, '/usr/lib/python3/dist-packages')
import pcbnew  # noqa: E402

OUT_PCB = "pcb/power-board/power-board.kicad_pcb"
OUT_PRO = "pcb/power-board/power-board.kicad_pro"
NETLIST = "pcb/power-board/power-board.net"

# Board outline: generous workspace for a power board that lives in the
# UMD cavity region; final size derives from cad/params.md (U1-U5 donor
# measurements pending, so this is an exploratory ESTIMATED envelope).
BOARD_W = 105.0
BOARD_H = 45.0


def parse_netlist(path):
    """Return {ref: {pin: netname}} and {netname: [(ref, pin), ...]}."""
    s = open(path, encoding="utf-8").read()
    pins_by_ref = {}
    nets = {}
    for m in re.finditer(r'\(net\s*\(code "\d+"\)\s*\(name "([^"]+)"\)(.*?)(?=\(net\s*\(code|\Z)',
                         s, re.S):
        name, body = m.groups()
        for nm in re.finditer(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', body):
            ref, pin = nm.groups()
            pins_by_ref.setdefault(ref, {})[pin] = name
            nets.setdefault(name, []).append((ref, pin))
    return pins_by_ref, nets


FP_LIB = "/usr/share/kicad/footprints"


def fp_path(nick, fp):
    return os.path.join(FP_LIB, f"{nick}.pretty", f"{fp}.kicad_mod")


# reference -> (lib nick, footprint name, x, y, rot)
# Positions are ESTIMATED exploratory placement (U1-U5 donor measurements
# pending); the co-design loop will move them.
PLACEMENT = {
    "J1": ("Connector_USB", "USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", 14.0, 22.0, 0),
    "U1": ("Package_DFN_QFN", "Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm", 30.0, 20.0, 0),
    "U2": ("Package_TO_SOT_SMD", "SOT-23-6", 42.0, 28.0, 0),
    "Q1": ("Package_TO_SOT_SMD", "SOT-23-6", 48.0, 28.0, 0),
    "J2": ("Connector_JST", "JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", 10.0, 32.0, 0),
    "U3": ("Package_DFN_QFN", "VQFN-16-1EP_3x3mm_P0.5mm_EP1.45x1.45mm", 42.0, 12.0, 0),
    "L1": ("Inductor_SMD", "L_0805_2012Metric", 34.0, 8.0, 0),
    "J3": ("Connector_PinHeader_2.54mm", "PinHeader_2x05_P2.54mm_Vertical", 50.0, 12.0, 90),
    "R1": ("Resistor_SMD", "R_0402_1005Metric", 26.0, 32.0, 0),
    "R2": ("Resistor_SMD", "R_0402_1005Metric", 28.0, 32.0, 0),
    "R3": ("Resistor_SMD", "R_0402_1005Metric", 30.0, 32.0, 0),
    "R4": ("Resistor_SMD", "R_0402_1005Metric", 32.0, 32.0, 0),
    "R5": ("Resistor_SMD", "R_0402_1005Metric", 34.0, 32.0, 0),
    "R6": ("Resistor_SMD", "R_0402_1005Metric", 24.0, 14.0, 0),
    "R7": ("Resistor_SMD", "R_0402_1005Metric", 26.0, 14.0, 0),
    "R8": ("Resistor_SMD", "R_0402_1005Metric", 28.0, 14.0, 0),
    "R9": ("Resistor_SMD", "R_0402_1005Metric", 30.0, 14.0, 0),
}

# net colors: which layer carries which class of net (F.Cu horizontal
# runs, B.Cu vertical). Power nets stay on F.Cu with wide tracks.
POWER_NETS = {"GND", "VBUS", "BAT", "SW33", "VOS33", "SW", "SYS", "PMID"}


def main():
    os.makedirs("pcb/power-board", exist_ok=True)
    pins_by_ref, nets = parse_netlist(NETLIST)
    if not nets:
        raise SystemExit("netlist parse failed - run kicad-cli sch export netlist first")

    board = pcbnew.CreateEmptyBoard()
    bpu = pcbnew.BOARD_UNITS_MM if hasattr(pcbnew, 'BOARD_UNITS_MM') else None

    # --- board outline (Edge.Cut rectangle) -------------------------------
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_RECT)
    edge.SetStart(pcbnew.VECTOR2I(int(2 * 1e6), int(2 * 1e6)))
    edge.SetEnd(pcbnew.VECTOR2I(int((2 + BOARD_W) * 1e6), int((2 + BOARD_H) * 1e6)))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(int(0.1 * 1e6))
    board.Add(edge)

    # --- nets --------------------------------------------------------------
    for name in nets:
        ni = board.FindNet(name)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)

    # --- footprints ---------------------------------------------------------
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    for ref, (nick, fp, x, y, rot) in PLACEMENT.items():
        path = fp_path(nick, fp)
        if not os.path.exists(path):
            print(f"!! footprint missing: {path}")
            continue
        f = io.FootprintLoad(os.path.join(FP_LIB, f"{nick}.pretty"), fp)
        if f is None:
            print(f"!! footprint load failed: {nick}/{fp}")
            continue
        f.SetReference(ref)
        f.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
        f.SetOrientationDegrees(rot)
        # assign pads to nets
        ref_pins = pins_by_ref.get(ref, {})
        for pad in f.Pads():
            num = pad.GetNumber()
            netname = ref_pins.get(num)
            if netname:
                ni = board.FindNet(netname)
                if ni is not None:
                    pad.SetNet(ni)
        board.Add(f)

    # keep the KiCad-10 rule constraints in the .kicad_pro (the schematic
    # generator rewrites the pro without them)
    import json
    pro = json.load(open(OUT_PRO))
    rules = pro.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
    rules.update({
        'min_hole_clearance': 0.15,
        'min_hole_to_hole': 0.2,
        'min_through_hole_diameter': 0.3,
        'min_via_diameter': 0.4,
        'min_copper_edge_clearance': 0.3,
    })
    json.dump(pro, open(OUT_PRO, 'w'), indent=2)

    board.Save(OUT_PCB)
    print(f"wrote {OUT_PCB} with {len(PLACEMENT)} footprints")


if __name__ == "__main__":
    main()
