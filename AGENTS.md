# Agent instructions

This repository contains the PSP-3000 internal hardware modification project.

## Design principles

- Treat PSP-3000 mechanical dimensions as hard design constraints, not something to fix after PCB design.
- Keep PCB, mechanical CAD, models, measurements, scripts, and documentation version-controlled.
- Prefer deterministic CLI/API operations over GUI automation.
- KiCad GUI / Computer Use may be used when CLI or IPC cannot perform the required operation.
- Never silently ignore ERC, DRC, missing footprints, missing 3D models, or mechanical collisions.
- Do not invent measurements. Record unknown dimensions explicitly and request/derive measurements before depending on them.
- Generated manufacturing/render/export files belong in `exports/`.

## Before considering a PCB change complete

1. Inspect `git diff`.
2. Run ERC when a schematic exists.
3. Run PCB DRC when a PCB exists.
4. Check board outline and mechanical constraints.
5. Export/check 3D geometry when mechanical fit is affected.
6. Commit coherent changes with a useful commit message.

## Git

Do substantial work on a feature branch rather than directly on `main`.
Do not destroy working designs merely to simplify an experiment.
Commit checkpoints before risky transformations.
