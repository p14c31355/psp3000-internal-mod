# Agent instructions

This repository contains the PSP-3000 internal hardware modification project.

## Work and evidence

- Never edit or commit directly on `main`. Start a feature branch or separate worktree before changing files. Do not force push or discard another person's work.
- Treat measured PSP-3000 mechanical dimensions, mounting points, connector positions, and clearance limits as design constraints before PCB layout. Record the measurement, units, source, tolerance, and coordinate reference in version control.
- Never guess an unknown dimension or silently substitute a nominal value. Mark it unknown, obtain a measurement or authoritative model, and block any dependent fit claim until then.
- Keep PCB, schematic, mechanical CAD, models, measurements, scripts, and documentation version controlled. Put generated reports and exports under `exports/`.
- Prefer deterministic CLI/API operations. Use the KiCad GUI only for steps that cannot be done reliably through CLI/API.
- Never suppress or silently ignore ERC/DRC violations, missing footprints or 3D models, STEP export failures, or collisions. Explain any accepted exception with evidence and review it in the diff.

## Required gate after every PCB or schematic change

1. Inspect `git diff` and `git status`; verify the branch is not `main`.
2. Run ERC for every affected schematic and DRC for every affected board, with violation exit codes. Fix violations or document an explicit, reviewed exception.
3. Inspect board outline, mounting holes, keepouts, connector placement, board thickness, and their measured mechanical constraints.
4. Export the board and populated 3D models to STEP. Verify required 3D models are present; a successful STEP export alone does not prove that.
5. Run FreeCAD interference checking against a measured, aligned enclosure or keepout solid. Record any collision and minimum clearance. If the enclosure model or alignment is missing, mark mechanical verification blocked; do not claim fit.
6. Inspect the final `git diff` and reports before committing coherent changes. Include the commands, inputs, versions, results, and unresolved limits in the handoff.

Use `scripts/verify-design.sh --schematic path --board path --enclosure path` when those inputs exist. The script writes reports to `exports/` and fails when a requested check fails. It does not replace visual inspection or evidence that 3D models and mechanical dimensions are complete.

## Long-running Goals

- Keep a long-running Goal active until its actual objective and required verification are complete. Do not mark it complete because a setup step, checkpoint, or token budget is nearly finished.
- Report what is verified and what is blocked. Pause or mark blocked only under the Goal's explicit status rules; do not turn uncertainty into a success claim.
