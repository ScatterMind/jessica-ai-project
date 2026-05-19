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
gh-pages branch as source). Both workflows run `scripts/build-dist.sh`
first — a hand-maintained **allowlist** that copies only the files
intended to deploy from `site/` into a runner-side `dist/` before
publishing. Anything in `site/` not listed in the script does not
deploy. Both workflows publish `dist/` (not `site/`); home page is
`site/index.html` + `site/banner.svg`. `corpus/` holds the
2026-05-17 Pilot Flying J pricing (XLS + README; proprietary)
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
`notes/route-planner-passcode.md` — `notes/` does not deploy (only
the build-dist.sh allowlist does), so it stays private to the repo.
Rotate via `web_build.py --passcode` and update that file in
lockstep. Note: `site/route-planner/README.md` is intentionally
**not** in the allowlist — kept as in-repo developer docs only.

Pages should be pointed at `gh-pages` branch / root in repo Settings.

## Planned layout (build as needed; not all up front)
- `site/` — public-deployable material (slides, marketing, polished
  docs). Files here only ship to the public Pages URL if they appear
  in the allowlist inside `scripts/build-dist.sh`. Be deliberate
  about adding to the allowlist — once a file is listed, it's
  world-readable at the deploy URL even though this repo is private.
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

## Web deploy
Pattern: daedalus model, allowlist build, gh-pages branch source.
- Pages source: `gh-pages` branch / root (Settings → Pages). Set
  once, manually.
- `.github/workflows/deploy-main.yml` — `main` → gh-pages root →
  `https://scattermind.github.io/jessica-ai-project/`
- `.github/workflows/deploy-dev.yml` — `dev` branch → `gh-pages/dev`
  → `https://scattermind.github.io/jessica-ai-project/dev/`
- Both workflows trigger on `site/**`, `scripts/build-dist.sh`, or
  their own workflow file changing. Both run `bash scripts/build-dist.sh`
  first to assemble the allowlisted `dist/`, then publish that.
- **Allowlist lives in `scripts/build-dist.sh`** as a literal block
  of `cp` commands. Adding a new public file = add a `cp` line,
  commit. Files in `site/` not listed are logged under "Files in
  site/ NOT deployed" in CI output so they stay visible.

## Do not publish (i.e. do not add to the build-dist.sh allowlist)
- Negotiation, compensation, or business-strategy material related
  to FIL's employer
- Anything from FIL's proprietary codebase or internal documents
- Personal communication or anything FIL hasn't explicitly cleared
  for outside eyes
- Add to this list as cases come up

(Items can still live in `site/` for build inputs — they just don't
get a `cp` line. Items that should never be in the repo at all
belong in `notes/` or `corpus/`.)

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

**2026-05-19 retrofit (meta session, no app code touched):** mirrored
`scattermind/meta` PR #17 — `.claude/settings.json` updated byte-identical
to new meta canonical (SessionStart hook now also cats `FUTURE.md`), and
a starter `FUTURE.md` added at repo root.

**2026-05-19 second pass (this PR):** the cross-Claude channels
(`## From meta` and `## For meta`) moved from FUTURE.md to this
HANDOFF (below the Meta AI section). Rationale: those are AI-to-AI
plumbing and belong in the AI-first file. No functional change —
same content, new location.

## Meta AI / cross-repo coordination

This repo is one of several under the `ScatterMind` GitHub account, organized by a **control-plane Claude session** in [`scattermind/meta`](https://github.com/ScatterMind/meta). Things to know:

- **`.claude/settings.json` is byte-identical across every ScatterMind repo.** Meta is canonical. If a hook needs editing, propose the change in `scattermind/meta` first, merge there, then mirror byte-for-byte here via a separate PR — never edit this file in isolation. (Meta HANDOFF "Daedalus drift incident" has the cautionary tale.)
- **Cross-Claude message channels live in this HANDOFF** (below). Two sections:
  - `## From meta` — meta-session writes allocated tasks or notes here. Read at session start for direction.
  - `## For meta` — write here when there's something meta should know. Meta reads at its next multi-repo session start (via `scattermind/meta/setup/multi-repo-prime.sh`, which extracts those two sections from each sibling HANDOFF).
- **Templates** for repeated repo shapes live in [`scattermind/meta/templates/`](https://github.com/ScatterMind/meta/tree/main/templates). Today: `templates/gh-pages/` (whitelist deploy YAMLs, static-`<PUBLISH_DIR>` shape). This repo's `scripts/build-dist.sh` allowlist is a shell-script variant of the same idea — meta's template README treats jessica-ai-project alongside daedalus and blinker as "variant to copy" pointers for build-time allowlist filtering. **No migration intended** for this repo.
- **Full meta-side rules** live in [`scattermind/meta/HANDOFF.md`](https://github.com/ScatterMind/meta/blob/main/HANDOFF.md). Worth skimming "Standard project repo structure", "Drift scan — standing meta-session task", and "Multi-repo meta session setup" once.

## From meta

_Meta-session writes here; this repo's per-repo Claude reads at SessionStart for direction. Don't delete entries without resolving them._

- **2026-05-19 — `scattermind/meta/templates/gh-pages/` exists.** Whitelist-style static-`<PUBLISH_DIR>` deploy template for new repos. Jessica-ai-project's existing **allowlist via `scripts/build-dist.sh`** (shipped 2026-05-18, PRs #4-#5) is a shell-script variant of the same idea — instead of a static `<PUBLISH_DIR>` the build script enumerates `cp` lines for each publishable file. Functionally equivalent guardrail; the meta template's README treats jessica-ai-project alongside daedalus and blinker as "real-world variants to copy from" for new repos that need build-time allowlist filtering. **No action required**: jessica-ai-project keeps its current pattern.
- **2026-05-19 — `.claude/settings.json` hook regex hardened (meta #22).** The Bash PreToolUse `git push` deny regex now also catches the `+main`/`+master` refspec force-push form (character class `[[:space:]:+]`, was `[[:space:]:]`). Found during tcs branch-protection testing: `git push origin +main` bypassed the hook because no space-or-colon preceded "main"; server-side protection caught it (HTTP 403) but the hook should be the first layer. This PR mirrors the byte-identical canonical to jessica-ai-project. **No action required**: behavior change only affects force-push attempts on main, which are blocked at both layers now.
- **2026-05-19 — FUTURE.md format rev2 (meta #23).** Canonical FUTURE.md shape evolved (proposal originated from daedalus's per-repo Claude). New shape: unified `## Backlog` (Goals + Next merged) + `## Archive` for ME-confirmed-done items (newest on top, kept indefinitely — manual prune only) + optional status tags (`[PARTIAL]`/`[QA-PENDING]`/`[BLOCKED]`; `[TODO]` is implicit and the tag can be omitted) alongside the existing ownership tags. This PR mirrors the format here; existing items moved from Goals/Next into Backlog with no content changes (just structural). **No action required**: format change only. Tags are optional — apply when status meaningfully differs from "not started."

## For meta

_This repo's per-repo Claude writes here when there's something meta should know — meta reads it at its next multi-repo session start._

(empty)
