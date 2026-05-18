# Handoff

## What this repo is
Workspace for supporting **Jessica AI** — my father-in-law's
trucking-company logistics platform. The product: Telegram chat UI
fronted by an LLM, with custom non-AI software doing the actual
logistics work underneath. **This repo is not the product** — it's
the support workspace: notes, research, prototype code, and
outward-facing material. Helps the product succeed and supports
FIL in negotiating fair compensation with his company.

## Current state
Fresh scaffold. Only the standard 4 files exist. No subdirs, no
workflows, no content. Build out per the layout below.

## Planned layout (build as needed; not all up front)
- `site/` — public-deployable material (slides, marketing, polished
  docs). Deploys to gh-pages. **Anything that lands here is
  world-readable** at the deploy URL even though this repo is
  private. Be deliberate.
- `notes/` — private workspace inside the private repo. Negotiation
  strategy, comp research, raw thinking. Never deploys.
- `src/` — code: scratch prototypes, tooling to help FIL move faster,
  fragments mirrored from his codebase for analysis.

## Web deploy (to set up — first per-repo session task)
Pattern: daedalus model.
- `.github/workflows/deploy-main.yml` — `main` → gh-pages root →
  `https://scattermind.github.io/jessica-ai-project/`
- `.github/workflows/deploy-dev.yml` — dev branch → `gh-pages/dev` →
  `https://scattermind.github.io/jessica-ai-project/dev/`
- After workflows merge, ask the user to enable GitHub Pages
  (Settings → Pages → source: gh-pages branch, root).

## Do not publish (i.e. do not place in `site/`)
- Negotiation, compensation, or business-strategy material related
  to FIL's employer
- Anything from FIL's proprietary codebase or internal documents
- Personal communication or anything FIL hasn't explicitly cleared
  for outside eyes
- Add to this list as cases come up

## Collaboration
**Solo workspace.** FIL is NOT a contributor — no read or write
access. If that ever changes, this section needs updating first
AND `notes/` content needs review before granting access. A future
session proposing to add FIL should pause and confirm with the user.

## Dev branch
None yet. First per-repo Claude session to do real work should create
one and record its name here.

## Standing rules
Destructive-action rules are enforced by hooks in
`.claude/settings.json` (byte-identical to meta canonical). The
HANDOFF-update rule is enforced by the Stop hook on real-work turns.
Read the SessionStart-injected context for the live list. Same
judgement-based update rules as every other ScatterMind repo.
