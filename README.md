# jessica-ai-project

Workspace for supporting Jessica AI — my father-in-law's
trucking-company logistics platform (Telegram chat UI + LLM front,
custom non-AI software underneath).

Planned layout (built out incrementally by per-repo AI sessions):
- `site/` — outward-facing material; an allowlisted subset deploys
  to GitHub Pages via the workflows in `.github/workflows/` and the
  literal `cp` list in `scripts/build-dist.sh`.
- `notes/` — private project notes, negotiation strategy, raw thinking.
- `src/` — prototype code, tooling, fragments from FIL's codebase for
  analysis.

See `VISION.md` for the why, `HANDOFF.md` for AI session context.
