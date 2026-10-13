"""Power board sizing simulation (provisional, pre-donor-measurement).

Semantics (fixed 2026-10-13):
- The only *verified* inner volume of the PSP-3000 after UMD-drive
  removal is the disc cavity: a UMD disc is 60 mm diameter and the
  drive must accept it, so the removed-drive cavity contains at least
  a 60 mm circle (DERIVED from the UMD spec, not donor-measured).
- This probe answers: what board outline fits inside that circle, and
  how does the current 105 x 45 mm power board compare?

This is a FEASIBILITY PROBE on placeholder geometry, NOT a fit claim.
Donor measurements U2 (UMD cavity extent) gate any real placement.

Run: freecadcmd cad/power_board_sizing_probe.FCMacro (copy of this file
inside repo; freecadcmd only executes .FCMacro extensions).
"""
import math

D = 60.0  # UMD disc diameter (mm), DERIVED from the UMD standard
R = D / 2.0


def max_rect_in_circle(w):
    """Given width w <= D, the max height h with the rect inside the circle."""
    if w >= D:
        return 0.0
    return 2.0 * math.sqrt(R * R - (w / 2.0) ** 2)


def main():
    print(f"UMD disc cavity (DERIVED): diameter {D:.0f} mm -> r {R:.0f} mm")
    print()
    print("Max rect fully inside the cavity circle:")
    for w in (30, 36, 40, 44, 48, 50, 52, 55):
        h = max_rect_in_circle(w)
        print(f"  w={w:2d} -> h_max={h:5.1f} mm   area={w*h:6.0f} mm2")
    print()
    cur_w, cur_h = 105.0, 45.0
    diag = math.hypot(cur_w, cur_h)
    print(f"Current power board: {cur_w:.0f} x {cur_h:.0f} mm "
          f"(diag {diag:.1f} mm) -> does NOT fit a {D:.0f} mm circle")
    print()
    # Candidate: two-board split.  The power functions split into a
    # charger board (USB-C + BQ25895 + protection) and a buck board
    # (TPS62130 + L + output header).  Charger board ~ 48x36 fits the
    # circle; buck board ~ 30x25 fits beside the Radxa in the main-body
    # zone (needs U1-U3 to confirm).
    print("Simulation result (PROVISIONAL):")
    print("  - charger board 48 x 36 mm fits the verified disc cavity")
    print("  - buck board (~30 x 25 mm) must live in the main-body zone,")
    print("    competing with the Radxa (65 x 30) for the same volume")
    print("  - both claims stay ESTIMATED until U2 (cavity extent) and")
    print("    U1-U3 (bosses, walls) are donor-measured")


main()
