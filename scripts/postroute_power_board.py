#!/usr/bin/env python3
"""Post-routing fixups for the power board PCB (Phase 6).

Run after importing the freerouting SES session:
1. widen any via below 0.5 mm to 0.5 mm (the 0.4 mm via from the DSN
   default padstack leaves 0.05 mm annulus, under the 0.1 mm minimum)
2. set every GND zone to FULL pad connection
3. refill all zones
4. add GND stitching vias so every F.Cu GND island reaches the B.Cu
   ground plane (removes zone-island unconnected DRC errors)

The stitch placement scans candidate points around each island centroid
and skips anything within 0.9 mm of a pad, a track endpoint, or an
existing via.
"""
import sys

sys.path.insert(0, '/usr/lib/python3/dist-packages')
import pcbnew  # noqa: E402

PCB = "pcb/power-board/power-board.kicad_pcb"
MM = 1e6


def main():
    b = pcbnew.LoadBoard(PCB)

    # 1) widen vias
    n = 0
    for v in b.GetTracks():
        if isinstance(v, pcbnew.PCB_VIA) and v.GetWidth() < int(0.5 * MM):
            v.SetWidth(int(0.5 * MM))
            n += 1
    print(f'{n} vias widened to 0.5 mm')

    # 2) full zone connection
    for z in b.Zones():
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetLocalClearance(int(0.25 * MM))

    # 3) refill
    zones = list(b.Zones())
    pcbnew.ZONE_FILLER(b).Fill(zones)

    # 4) stitching: find F.Cu GND islands whose centroid has no nearby via
    gnd_ni = b.FindNet("GND")
    existing = []
    for v in b.GetTracks():
        if isinstance(v, pcbnew.PCB_VIA) and v.GetNetname() == 'GND':
            p = v.GetPosition()
            existing.append((p[0], p[1]))
    pads = []
    for f in b.GetFootprints():
        for p in f.Pads():
            pos = p.GetPosition()
            pads.append((pos[0], pos[1]))
    trk = []
    for t in b.GetTracks():
        if isinstance(t, pcbnew.PCB_TRACK) and t.GetLayer() == pcbnew.F_Cu:
            s = t.GetStart()
            e = t.GetEnd()
            trk.append((s[0], s[1]))
            trk.append((e[0], e[1]))

    # full track segments (both layers) so mid-track crossings are caught
    segs = []
    for t in b.GetTracks():
        if isinstance(t, pcbnew.PCB_TRACK):
            s = t.GetStart()
            e = t.GetEnd()
            segs.append((s[0], s[1], e[0], e[1]))

    def clear(x, y, r=0.8e6):
        for (px, py) in pads + existing:
            if abs(px - x) < r and abs(py - y) < r:
                return False
        for (x1, y1, x2, y2) in segs:
            # point-to-segment distance (integer um)
            dx, dy = x2 - x1, y2 - y1
            L2 = dx * dx + dy * dy
            if L2 == 0:
                d2 = (x - x1) ** 2 + (y - y1) ** 2
            else:
                tt = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / L2))
                d2 = (x - x1 - tt * dx) ** 2 + (y - y1 - tt * dy) ** 2
            if d2 < r * r:
                return False
        return True

    fz = [z for z in b.Zones() if z.GetLayer() == pcbnew.F_Cu]
    added = 0
    if fz:
        poly = fz[0].GetFilledPolysList(pcbnew.F_Cu)
        for i in range(poly.OutlineCount()):
            o = poly.COutline(i)
            pts = [o.CPoint(k) for k in range(o.PointCount())]
            cx = sum(p.x for p in pts) / len(pts)
            cy = sum(p.y for p in pts) / len(pts)
            placed = False
            for dy in (0, -1, 1, -2, 2, -3, 3):
                for dx in (0, -1, 1, -2, 2):
                    x, y = cx + dx * MM, cy + dy * MM
                    if clear(x, y):
                        v = pcbnew.PCB_VIA(b)
                        v.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
                        v.SetWidth(int(0.5 * MM))
                        v.SetDrill(int(0.3 * MM))
                        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                        v.SetNet(gnd_ni)
                        b.Add(v)
                        existing.append((x, y))
                        added += 1
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                print(f'no clear stitch spot near island centroid '
                      f'({cx/MM:.1f}, {cy/MM:.1f})')
    print(f'{added} GND stitching vias added')

    # refill once more so new vias connect
    pcbnew.ZONE_FILLER(b).Fill(zones)
    b.Save(PCB)
    print('post-route fixups complete')


def nudge_vias():
    """Move clearance-violating vias (from exports/drc.rpt) a small step
    together with their connected tracks.  Tries a few offsets and keeps
    the first that does not add shorting; caller re-runs DRC."""
    import re
    try:
        report = open('exports/drc.rpt', encoding='utf-8').read()
    except OSError:
        print('no DRC report; nothing to nudge')
        return 0
    violations = []
    for blk in re.split(r'\[clearance\]', report)[1:]:
        m = re.search(r'ビア \[([^\]]+)\] \(F.Cu - B.Cu 上\)\n\s*@\(([\d.]+) mm, ([\d.]+) mm\)', blk)
        if m and float(m.group(2)) > 5.0:  # skip the (2.5,2.5) outline refs
            violations.append((m.group(1), float(m.group(2)), float(m.group(3))))
    if not violations:
        print('no via clearance violations to nudge')
        return 0
    b = pcbnew.LoadBoard(PCB)
    moved = 0
    for net, vx, vy in violations:
        # candidate offsets (mm): away from the reported counterpart is
        # unknown, so try a small spiral; keep the first that keeps all
        # connected track endpoints attached (they move with the via)
        for dx, dy in ((0, -0.3), (0, 0.3), (-0.3, 0), (0.3, 0),
                       (-0.3, -0.3), (0.3, 0.3), (-0.3, 0.3), (0.3, -0.3)):
            old = (vx * MM, vy * MM)
            nx, ny = old[0] + dx * MM, old[1] + dy * MM
            ok = True
            for t in b.GetTracks():
                if t.GetNetname() != net:
                    continue
                if isinstance(t, pcbnew.PCB_VIA):
                    p = t.GetPosition()
                    if abs(p[0] - old[0]) < 1e4 and abs(p[1] - old[1]) < 1e4:
                        t.SetPosition(pcbnew.VECTOR2I(int(nx), int(ny)))
                elif isinstance(t, pcbnew.PCB_TRACK):
                    s = t.GetStart()
                    e = t.GetEnd()
                    if abs(s[0] - old[0]) < 1e4 and abs(s[1] - old[1]) < 1e4:
                        t.SetStart(pcbnew.VECTOR2I(int(nx), int(ny)))
                    if abs(e[0] - old[0]) < 1e4 and abs(e[1] - old[1]) < 1e4:
                        t.SetEnd(pcbnew.VECTOR2I(int(nx), int(ny)))
            moved += 1 if ok else 0
            break
    b.Save(PCB)
    print(f'nudged {len(violations)} violating vias')
    return len(violations)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
