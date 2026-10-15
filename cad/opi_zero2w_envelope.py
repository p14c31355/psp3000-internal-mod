"""Orange Pi Zero 2W mechanical envelope model.

Generates cad/steps/orangepi_zero2w_envelope.step - a placeholder
envelope derived ONLY from verified dimensions.  Per AGENTS.md this is
not a fit claim: hole positions are ESTIMATED (U15) and component
heights are ESTIMATED from board photos.

Verified (Orange Pi User Manual v1.1):
  board outline 65 x 30 mm, thickness 1.2 mm, 4x 3.0 mm positioning
  holes, weight 12.5 g.

Estimated (U15 will replace):
  hole positions 3.5 mm inset from corners (Raspberry Pi Zero family
  pattern); component envelope 5.0 mm above board top over the full
  outline (governing item: TF slot and USB-C shells); 1.5 mm below
  (solder joints).

Usage (freecadcmd treats .py as a REPL - run as .FCMacro per repo rule):
  cp cad/opi_zero2w_envelope.py /tmp/o.FCMacro && freecadcmd /tmp/o.FCMacro
"""
import FreeCAD as App
import Part

L = 65.0   # verified
W = 30.0   # verified
T = 1.2    # verified
HOLE_D = 3.0   # verified
HOLE_INSET = 3.5   # ESTIMATED (U15)
TOP_ENV = 5.0  # ESTIMATED component height envelope
BOT_ENV = 1.5  # ESTIMATED

doc = App.newDocument("opi")

board = doc.addObject("Part::Box", "board")
board.Length, board.Width, board.Height = L, W, T

# component envelope above and below the board (for clearance sims)
top = doc.addObject("Part::Box", "top_envelope")
top.Length, top.Width, top.Height = L, W, TOP_ENV
top.Placement = App.Placement(App.Vector(0, 0, T), App.Rotation())

bot = doc.addObject("Part::Box", "bottom_envelope")
bot.Length, bot.Width, bot.Height = L, W, BOT_ENV
bot.Placement = App.Placement(App.Vector(0, 0, -BOT_ENV), App.Rotation())

# holes as cuts through board only (they are mounting holes, the
# envelopes represent components)
holes = []
for x in (HOLE_INSET, L - HOLE_INSET):
    for y in (HOLE_INSET, W - HOLE_INSET):
        c = doc.addObject("Part::Cylinder", "hole_%s_%s" % (x, y))
        c.Radius, c.Height = HOLE_D / 2.0, T + 2.0
        c.Placement = App.Placement(
            App.Vector(x, y, -1.0), App.Rotation())
        holes.append(c)

board_cut = board
for i, h in enumerate(holes):
    cut = doc.addObject("Part::Cut", "board_cut%d" % i)
    cut.Base = board_cut
    cut.Tool = h
    board_cut = cut

doc.recompute()

import Import
Import.export([board_cut, top, bot],
              "cad/steps/orangepi_zero2w_envelope.step")
print("STEP written: cad/steps/orangepi_zero2w_envelope.step")
print("outline %sx%sx%s (VERIFIED), holes d%s at %smm inset (ESTIMATED U15)"
      % (L, W, T, HOLE_D, HOLE_INSET))
print("envelope above %smm, below %smm (ESTIMATED U15)" % (TOP_ENV, BOT_ENV))
