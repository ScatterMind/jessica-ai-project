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
Deploy scaffold landed: `.github/workflows/deploy-main.yml` and
`deploy-dev.yml` (daedalus pattern, peaceiris/actions-gh-pages@v4,
gh-pages branch as source), plus `site/index.html` (banner + link
tile to the route planner) and `site/banner.svg`. `corpus/` holds
the 2026-05-17 Pilot Flying J pricing (XLS + README; proprietary)
plus `corpus/geo/us_cities.csv` (public, MIT) used by code in `src/`.

`src/fuel_optimizer/` — gas-price-optimal refueling planner
(Khuller-Malekian-Mestre greedy). CLI with a built-in sample route
set; sample output at `corpus/pilot-flying-j/2026-05-17/optimized-routes.md`.
`src/fuel_optimizer/web_build.py` builds the encrypted bundle that
the route planner serves: AES-GCM blob (`site/route-planner/data.enc.json`)
+ a copy of the public cities CSV. Rebuild on each new pricing drop;
the script prints a fresh random passcode to stderr if `--passcode`
isn't given.

`site/route-planner/` is the public-facing static app: HTML +
Leaflet + Web Crypto + OSRM driving directions + the JS-ported
optimizer. The encrypted blob ships in the deployed bundle; without
the passcode the data is unreadable. Passcode lives at
`notes/route-planner-passcode.md` — `notes/` does not deploy
(`.github/workflows/deploy-main.yml` only publishes `./site`), so
it stays private to the repo. Rotate via `web_build.py --passcode`
and update that file in lockstep.

Pages should be pointed at `gh-pages` branch / root in repo Settings.

## Planned layout (build as needed; not all up front)
- `site/` — public-deployable material (slides, marketing, polished
  docs). Deploys to gh-pages. **Anything that lands here is
  world-readable** at the deploy URL even though this repo is
  private. Be deliberate.
- `corpus/` — reference documents that inform project development:
  vendor reports, data dumps, fragments of source material to be
  analyzed. Private, never deploys. Distinct from `notes/` (raw
  thinking) and `src/` (code). Use date-stamped subfolders under a
  source key (e.g. `corpus/<source>/<YYYY-MM-DD>/`) so recurring
  drops slot in the same shape.
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
`dev` — long-lived staging branch that `deploy-dev.yml` watches
(publishes `site/` to `gh-pages/dev/`). Not yet created; first
session that needs a staging deploy creates it off `main`.

This session's own work happened on the system-assigned
`claude/setup-project-scaffold-TzrW2`, PR'd straight to `main`
(no staging needed for the scaffold itself).

## Standing rules
Destructive-action rules are enforced by hooks in
`.claude/settings.json` (byte-identical to meta canonical). The
HANDOFF-update rule is enforced by the Stop hook on real-work turns.
Read the SessionStart-injected context for the live list. Same
judgement-based update rules as every other ScatterMind repo.
