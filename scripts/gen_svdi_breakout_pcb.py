"""Generate the SVDI breakout PCB via the pcbnew Python API (headless).

Layout v3 (DRC-driven): J1 FPC row on top, J2 header column on the right.
Routing plan per net n (1..31):
  1. F.Cu stub: J1 pad -> (pad_x, y_via1(n)) with staggered via rows
     (even/odd offset) so adjacent 0.5 mm-pitch vias keep >= 0.28 mm edge gap.
  2. via1 (0.4 mm dia, 0.2 mm drill).
  3. B.Cu vertical: via1 -> (pad_x, y2(n)) — verticals at distinct 0.5 mm
     columns, 0.15 mm wide (0.35 mm gap >= 0.2 clearance).
  4. via2 = the B.Cu vertical's lower end at (pad_x, y2(n)).
  5. F.Cu horizontal at y2(n) from pad_x rightward to the J2 PTH pad —
     rows are 1.27 mm apart and never overlap the F.Cu stub y-range.
Layer split means B.Cu verticals never interact with F.Cu horizontals.

Run: .venv/bin/python scripts/gen_svdi_breakout_pcb.py
"""
import os
import re
import sys

sys.path.insert(0, "/usr/lib/python3/dist-packages")
import pcbnew  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(ROOT, "pcb", "svdi-breakout", "svdi-breakout.kicad_pcb")
SCH = os.path.join(ROOT, "pcb", "svdi-breakout", "svdi-breakout.kicad_sch")

FPC_FP = ("Connector_FFC-FPC:Amphenol_F32Q-1A7x1-11031_"
          "1x31-1MP_P0.5mm_Horizontal")
HDR_FP = "Connector_PinHeader_1.27mm:PinHeader_1x40_P1.27mm_Vertical"


def mm(x):
    return pcbnew.FromMM(x)


def main():
    netlist = os.path.join(ROOT, "pcb", "svdi-breakout", "svdi-breakout.net")
    if not os.path.exists(netlist):
        os.system(f"kicad-cli sch export netlist --output {netlist} {SCH}")

    net_text = open(netlist).read()
    nets = {}
    for m in re.finditer(
            r'\(net\s*\n\s*\(code "\d+"\)\s*\n\s*\(name "([^"]+)"\)(.*?)(?=\n\t\t\(net\n|\n\t\)\n\t\)\n)',
            net_text, re.S):
        name, body = m.group(1), m.group(2)
        conns = re.findall(r'\(ref "([^"]+)"\)\s*\n\s*\(pin "([^"]+)"\)', body)
        nets[name] = conns

    board = pcbnew.CreateEmptyBoard()
    net_map = {}
    for name in nets:
        item = pcbnew.NETINFO_ITEM(board, name)
        board.Add(item)
        net_map[name] = item

    loader = pcbnew.PCB_IO_KICAD_SEXPR()

    def load_fp(desc, ref, x_mm, y_mm, rot=0):
        lib, name = desc.split(":", 1)
        fp = loader.FootprintLoad(
            f"/usr/share/kicad/footprints/{lib}.pretty", name)
        fp.SetReference(ref)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x_mm), mm(y_mm)))
        fp.SetOrientationDegrees(rot)
        board.Add(fp)
        return fp

    fpc = load_fp(FPC_FP, "J1", 30.0, 42.1, rot=0)
    hdr = load_fp(HDR_FP, "J2", 90.0, 45.0, rot=0)
    # drop J2 so its first pad sits 3 mm below the lowest J1 pad
    j1_pads_probe = [fpc.FindPadByNumber(str(n)).GetPosition()
                     for n in range(1, 32)]
    j2_pad1 = hdr.FindPadByNumber("1").GetPosition()
    target_y = max(p.y for p in j1_pads_probe) + mm(3.0)
    hdr.SetPosition(hdr.GetPosition() + pcbnew.VECTOR2I(0, target_y - j2_pad1.y))

    for name, conns in nets.items():
        for ref, pin in conns:
            target = fpc if ref == "J1" else hdr
            pad = target.FindPadByNumber(pin)
            if pad is not None:
                pad.SetNet(net_map[name])

    fpc_bb = fpc.GetBoundingBox()
    hdr_bb = hdr.GetBoundingBox()
    margin = mm(4.0)
    x0 = min(fpc_bb.GetLeft(), hdr_bb.GetLeft()) - margin
    y0 = min(fpc_bb.GetTop(), hdr_bb.GetTop()) - margin
    x1 = max(fpc_bb.GetRight(), hdr_bb.GetRight()) + margin
    y1 = max(fpc_bb.GetBottom(), hdr_bb.GetBottom()) + margin

    ds = pcbnew.PCB_SHAPE(board)
    ds.SetShape(pcbnew.SHAPE_T_RECT)
    ds.SetStart(pcbnew.VECTOR2I(x0, y0))
    ds.SetEnd(pcbnew.VECTOR2I(x1, y1))
    ds.SetLayer(pcbnew.Edge_Cuts)
    ds.SetWidth(mm(0.1))
    board.Add(ds)

    track_w = mm(0.2)
    vert_w = mm(0.2)
    via_dia = mm(0.5)
    via_drill = mm(0.3)

    def seg(ax, ay, bx, by, width, layer, netcode):
        if ax == bx and ay == by:
            return
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(ax, ay))
        t.SetEnd(pcbnew.VECTOR2I(bx, by))
        t.SetWidth(width)
        t.SetLayer(layer)
        t.SetNetCode(netcode)
        board.Add(t)

    def via(x, y, netcode):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(x, y))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetWidth(via_dia)
        v.SetDrill(via_drill)
        v.SetNetCode(netcode)
        board.Add(v)

    # Routing: layer-split switchbox v5 (final). F.Cu: vertical stub per
    # J1 pad down to via1 at y=41.5 (0.35 mm via, 0.5 mm pitch: copper gap
    # 0.15, hole gap 0.3); multi-pin nets (COM, NC, VS) extend their stubs
    # up to y=38.75 where a tie joins them into a single island. One F.Cu
    # horizontal per net at its J2 pad row lands directly on the plated pad.
    # B.Cu carries only verticals. Stubs end at 41.5; the shallowest J2 row
    # is 42.2, so horizontals never touch stubs of other nets.
    track_w = mm(0.2)
    via_dia = mm(0.35)
    via_drill = mm(0.2)
    via1_y = mm(41.5)

    # collect per-net J1 pins to know which stubs need the upper tie
    net_pins = {}
    for n in range(1, 32):
        p1 = fpc.FindPadByNumber(str(n))
        net_pins.setdefault(p1.GetNetname(), []).append(n)
    # staggered tie rows, widest span highest, so a tie never crosses a
    # stub of another multi-pin net (narrower nets start lower)
    tie_y_of = {}
    multi = [(name, pins) for name, pins in net_pins.items() if len(pins) > 1]
    multi.sort(key=lambda item: -(max(item[1]) - min(item[1])))
    next_tie = 37.1
    for net_name, pins in multi:
        tie_y_of[net_name] = mm(next_tie)
        next_tie += 0.35

    for n in range(1, 32):
        p1 = fpc.FindPadByNumber(str(n))
        p2 = hdr.FindPadByNumber(str(n))
        if p1 is None or p2 is None:
            continue
        code = p1.GetNetCode()
        px, py = int(p1.GetPosition().x), int(p1.GetPosition().y)
        tx, ty = int(p2.GetPosition().x), int(p2.GetPosition().y)
        # F.Cu stub: start at the net's tie row (covers the pad on the way down)
        tie = tie_y_of.get(p1.GetNetname())
        top_y = int(tie) if tie is not None else py
        seg(px, top_y, px, via1_y, track_w, pcbnew.F_Cu, code)
        via(px, via1_y, code)
        # B.Cu vertical down to the net's J2 row
        seg(px, via1_y, px, ty, track_w, pcbnew.B_Cu, code)
        via(px, ty, code)
        # F.Cu horizontal straight into the plated pad
        seg(px, ty, tx, ty, track_w, pcbnew.F_Cu, code)

    # upper ties for multi-pin nets (one per net, on its own staggered row)
    for net_name, pins in net_pins.items():
        if net_name not in tie_y_of:
            continue
        code = net_map[net_name].GetNetCode()
        xs = [int(fpc.FindPadByNumber(str(n)).GetPosition().x) for n in pins]
        seg(min(xs), tie_y_of[net_name], max(xs), tie_y_of[net_name],
            track_w, pcbnew.F_Cu, code)

    filler = pcbnew.ZONE(board)
    filler.SetLayer(pcbnew.B_Cu)
    filler.SetNetCode(net_map["/GND"].GetNetCode() if "/GND" in net_map else 0)
    filler.SetIsFilled(False)
    outline = filler.Outline()
    chain = outline.Outline(outline.NewOutline())
    chain.Append(x0, y0)
    chain.Append(x1, y0)
    chain.Append(x1, y1)
    chain.Append(x0, y1)
    board.Add(filler)

    board.BuildListOfNets()
    # Bench-tool fabrication class: the Default netclass gets 0.4 mm vias
    # with 0.2 mm drills and keeps the 0.2 mm track/clearance minima, so the
    # staggered 0.4 mm escape vias are inside the board's own rules.
    netclass = board.GetDesignSettings().m_NetSettings.GetDefaultNetclass()
    netclass.SetViaDiameter(mm(0.4))
    netclass.SetViaDrill(mm(0.2))
    # Board-level minima must match the bench fabrication class or DRC
    # rejects the 0.4 mm vias outright.
    design = board.GetDesignSettings()
    design.m_ViasMinSize = mm(0.4)
    design.m_MinThroughDrill = mm(0.2)
    pcbnew.ZONE_FILLER(board).Fill([filler])
    board.Save(PCB)
    print("saved", PCB)

    n_pads = sum(1 for p in fpc.Pads() if p.GetNetCode() > 0)
    n_pads += sum(1 for p in hdr.Pads() if p.GetNetCode() > 0)
    print("pads with nets:", n_pads)


if __name__ == "__main__":
    main()
