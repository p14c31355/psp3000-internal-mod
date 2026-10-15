# BitBuilt PSP-3000 3D scan — mesh analysis (mechanical reference)

Source: BitBuilt forum thread 7305 (Wesk's third-party PSP-3000 scans,
Ko-fi funded).  Downloaded 2026-10-15 from
`https://bitbuilt.net/wesk/3D%20Scans/PSP%203000.zip`.

**Provenance and limits (binding):**
- This is a **3rd-party shell scan**, NOT our Japanese PSP-3000 unit.
  Differences from OEM are possible and unquantified.  Class for every
  number below: **REFERENCE_SCAN** — usable for topology/structure
  planning, never as a manufacturing constraint for OUR unit.
- High-poly scans (0.8-1.25 M triangles per part, 433 MB total).  Kept
  as meshes under `cad/references/bitbuilt-psp3000/scan/` (gitignored
  content — see below); never converted blindly to B-rep.

## Mesh inventory (as-scanned coordinates, mm)

| Part | Triangles | Dims (X×Y×Z) | Notes |
|---|---|---|---|
| front | 2,004,574 | 168.16 × 70.94 × 13.20 | scanned with the front glass installed |
| rear | 2,494,742 | 168.24 × 70.56 × 17.35 | includes bosses; tallest point 17.35 |
| UMD Lid | 2,504,882 | 72.94 × 70.47 × 14.11 | thin shell: ~60% of vertices ≤1 mm thick |
| Battery Lid | 1,652,150 | 70.06 × 47.85 × 6.18 | |

Scale check: front/rear X ≈ 168.2 mm vs the 169.4 mm Sony spec — the
scan is at true mm scale (small shrinkage/scan noise within ~1%).
The coordinate origins differ per part (each scanned separately); a
global alignment (per the owner's 7-item list) is still required.

## What the Z-profiles establish

Analysis method: 1-2 mm XY grid, per-cell Z max (rear) / Z min
(front); ASCII heatmaps and `.npy` arrays kept in the analysis dir.

1. **Rear shell (battery-side up)**
   - Battery bay region floor rim: zmax ≈ 4.2 mm (the bay's rim sits
     ~4 mm above the scan datum).
   - UMD cavity region: rim heights 8.8-14.4 mm — the cavity walls'
     top edge band.  Consistent with the door-trough architecture.
   - Screw bosses: 12 clusters above z=16 mm, tallest **17.35 mm at
     (y=58, x=30) in scan coordinates** (rear, left-of-center).
     These are the structural keepouts — cross-check against the
     photo analysis (`photo-analysis-donor-shell.md`) before cutting.
2. **UMD Lid**: predominantly a thin shell (z histogram peaks 0-1 mm)
   with local thickening to 14 mm — the hinge/latch reinforcement.
   Confirms the door itself consumes almost no cavity depth; the
   depth budget is door-trough walls, not the lid.
3. **Front shell**: scanned **with glass installed** — the glass
   covers the whole front (a continuous 2.2-2.8 mm low plateau across
   x=32..136 at mid-height, tilted top-to-bottom 2.8→2.2).  The
   physical display window (black bezel opening) is a COLOR boundary,
   not a Z boundary, so this scan cannot locate the window edge.
   Window XY must come from the skeleton-shell photos (U13) or our
   unit; the glass outer profile here feeds the U12 stack budget:
   **glass outer surface ≈ 2.2-2.8 mm above the front-shell datum.**

## Implications for the v2 mechanical layout

- The Ø60-inscribed-circle model is retired; cavity planning moves to
  the scanned rear-shell profile (rounded-square opening per photos,
  walls 8.8-14.4 mm tall) once the scan is aligned to our coordinate
  system.
- OP-B (split-z in the cavity) gets its first real Z numbers: cavity
  wall band 8.8-14.4 mm vs OPi envelope 1.2 + ~5 mm parts.  Alignment
  study is the next FreeCAD step.
- The front glass datum (~2.2-2.8 mm) tightens the display stack:
  module + bridge must fit in (aperture depth) minus (glass-to-datum
  ~2.5 mm).  U12 physical measurement remains the gate.

## Files

- `scan/*.stl` — original meshes, untouched (not committed; 433 MB,
  see `.gitignore`).  Re-download via the URL above if lost.
- `mesh-bounds.txt` — per-part bbox summary (committed).
- Analysis arrays: `/tmp/rear_zmax.npy`, `/tmp/front_zmin1.npy`
  (regenerable; scripts inline in session history — promote to
  `cad/` scripts when the alignment work starts).

## Next steps

1. Global alignment: ICP-free datum choice — put front+rear in the
   Sony body coordinate system (origin bottom-left of front face, X
   right, Y up, Z toward viewer, per MEASUREMENT-PLAN) using the
   shared perimeter.
2. Import into FreeCAD as mesh references; build simplified keepout
   solids: bosses (cylinders), battery bay, UMD cavity walls, glass
   datum plane.
3. xovi printable kit (secondary reference): Cloudflare blocks direct
   STL fetch by curl; fetch via browser tool next — its "modding-
   friendly extra back space" documents which internal structures are
   truly required.
