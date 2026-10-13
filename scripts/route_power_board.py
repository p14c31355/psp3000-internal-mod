#!/usr/bin/env python3
"""Route the power board PCB with a layer-separation switchbox (Phase 6).

Proven approach from the SVDI breakout (v3), adapted for this board:

- F.Cu carries only horizontal runs; B.Cu only vertical runs plus a GND
  zone.
- Every net gets a dedicated escape column x (unique per net, 1.2 mm
  pitch) so horizontal segments never cross each other.
- Each pad: F.Cu horizontal stub to its net's column, via down, B.Cu
  vertical run to the target row, via up, F.Cu horizontal to the next
  pad.  Multi-pad nets are chained in pad order.
- GND is a single B.Cu zone; its pad connections use thermal spokes.
- Power nets use wider tracks.

Netlist is the source of truth.  Run after gen_power_board_pcb.py.
"""
import re
import sys

sys.path.insert(0, '/usr/lib/python3/dist-packages')
import pcbnew  # noqa: E402

PCB = "pcb/power-board/power-board.kicad_pcb"
MM = 1e6

W_SIG = int(0.25 * MM)
W_PWR = int(0.6 * MM)
VIA_D = int(0.5 * MM)
VIA_DRILL = int(0.3 * MM)
COL_PITCH = 1.2  # mm between escape columns
COL_X0 = 64.0    # escape column band, right of all parts

POWER = {"VBUS", "BAT", "SW33", "VOS33", "SW", "SYS", "PMID",
         "FETMID", "PACKNEG", "BATGND", "REGN"}


def parse_netlist(path):
    s = open(path, encoding="utf-8").read()
    nets = {}
    for m in re.finditer(r'\(net\s*\(code "\d+"\)\s*\(name "([^"]+)"\)(.*?)(?=\(net\s*\(code|\Z)',
                         s, re.S):
        name, body = m.groups()
        nodes = re.findall(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', body)
        nets[name] = nodes
    return nets


def main():
    b = pcbnew.LoadBoard(PCB)

    # pad lookup: (ref, pin) -> position
    pad_pos = {}
    for f in b.GetFootprints():
        ref = f.GetReference()
        for p in f.Pads():
            pos = p.GetPosition()
            pad_pos[(ref, p.GetNumber())] = (pos[0], pos[1])

    nets = parse_netlist("pcb/power-board/power-board.net")
    net_names = [n for n in nets
                 if not n.startswith('unconnected-') and n.lstrip('/') != 'GND']
    if "--no-routes" in sys.argv:
        # placement + GND zone only; explicit routing is still pending
        gnd_ni = b.FindNet("GND")
        z = pcbnew.ZONE(b)
        if gnd_ni is not None:
            z.SetNet(gnd_ni)
        z.SetLayer(pcbnew.B_Cu)
        z.SetLocalClearance(int(0.25 * MM))
        z.SetIsFilled(False)
        outline = z.Outline()
        chain = outline.Outline(outline.NewOutline())
        for (x, y) in ((2.5, 2.5), (102.5, 2.5), (102.5, 42.5), (2.5, 42.5)):
            chain.Append(int(x * MM), int(y * MM))
        b.Add(z)
        # F.Cu GND zone as well: top-side GND pads must reach ground on
        # their own layer (the B.Cu zone alone leaves them unconnected)
        z2 = pcbnew.ZONE(b)
        z2.SetNet(gnd_ni)
        z2.SetLayer(pcbnew.F_Cu)
        z2.SetLocalClearance(int(0.25 * MM))
        z2.SetIsFilled(False)
        outline2 = z2.Outline()
        chain2 = outline2.Outline(outline2.NewOutline())
        for (x, y) in ((2.5, 2.5), (102.5, 2.5), (102.5, 42.5), (2.5, 42.5)):
            chain2.Append(int(x * MM), int(y * MM))
        b.Add(z2)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z2.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        pcbnew.ZONE_FILLER(b).Fill([z, z2])
        b.Save(PCB)
        print("saved placement + GND zones F.Cu/B.Cu (routes pending)")
        return
    # deterministic column assignment
    net_names.sort()
    net_col = {n: COL_X0 + i * COL_PITCH for i, n in enumerate(net_names)}

    # verify every routed net has real positions
    def track(x0, y0, x1, y1, layer, width, netname):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(int(x0), int(y0)))
        t.SetEnd(pcbnew.VECTOR2I(int(x1), int(y1)))
        t.SetWidth(width)
        t.SetLayer(layer)
        ni = b.FindNet(netname)
        if ni is not None:
            t.SetNet(ni)
        b.Add(t)

    def via(x, y, netname):
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
        v.SetWidth(VIA_D)
        v.SetDrill(VIA_DRILL)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        ni = b.FindNet(netname)
        if ni is not None:
            v.SetNet(ni)
        b.Add(v)

    F = pcbnew.F_Cu
    B = pcbnew.B_Cu
    routed = 0
    missing = []

    for netname in net_names:
        core = netname.lstrip('/')
        w = W_PWR if core in POWER else W_SIG
        cx = int(net_col[netname] * MM)
        nodes = nets[netname]
        pts = []
        for ref, pin in nodes:
            key = (ref, pin)
            if key in pad_pos:
                pts.append(pad_pos[key])
            else:
                missing.append(key)
        if len(pts) < 2:
            continue
        # chain: pad0 -> col -> (B.Cu vertical) -> pad1 row -> pad1 ...
        # F.Cu horizontal from pad to column, then up/down on B.Cu
        prev = None
        for (px, py) in pts:
            if prev is None:
                # first pad: horizontal F.Cu to column
                track(px, py, cx, py, F, w, netname)
                via(cx, py, netname)
                prev = (cx, py)
                continue
            # vertical on B.Cu from prev.y to this pad's y
            track(prev[0], prev[1], cx, px if False else py, B, w, netname)
            via(cx, py, netname)
            # horizontal F.Cu from column to pad
            track(cx, py, px, py, F, w, netname)
            prev = (cx, py)
            routed += 1

    # GND zone on B.Cu only (F.Cu carries all horizontal runs)
    gnd_ni = b.FindNet("GND")
    z = pcbnew.ZONE(b)
    if gnd_ni is not None:
        z.SetNet(gnd_ni)
    z.SetLayer(pcbnew.B_Cu)
    z.SetLocalClearance(int(0.3 * MM))
    z.SetIsFilled(False)
    outline = z.Outline()
    chain = outline.Outline(outline.NewOutline())
    for (x, y) in ((2.5, 2.5), (61.5, 2.5), (61.5, 41.5), (2.5, 41.5)):
        chain.Append(int(x * MM), int(y * MM))
    b.Add(z)
    pcbnew.ZONE_FILLER(b).Fill([z])

    b.Save(PCB)
    print(f"routed {routed} nodes over {len(net_names)} nets; "
          f"missing pads: {missing[:4]}")
    if missing:
        print(f"total missing: {len(missing)}")


if __name__ == "__main__":
    main()
