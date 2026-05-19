# Future

Forward-looking notes for jessica-ai-project. Vague goals, queued
work, and cross-Claude message channels.

This is the **human-facing** roadmap; HANDOFF.md is the AI's
internal notebook. Some redundancy between them is fine.

## How this file works

- Anyone (you, this repo's per-repo Claude, the meta-session Claude)
  can append. Mark ownership inline when it matters: `[ME]` /
  `[AI]` / `[HYBRID]`.
- `## From meta` — meta-session writes allocated tasks or notes
  here. The per-repo Claude reads it at session start for direction.
- `## For meta` — the per-repo Claude writes here when there's
  something meta should know. Meta reads at its next multi-repo
  session start (via `scattermind/meta/setup/multi-repo-prime.sh`).
- When work happens, record it in HANDOFF.md and prune / update
  the matching FUTURE entry. Keep this file short.

## Goals

(open-ended; vague is OK — promote to Next when shape sharpens)

- Help FIL succeed on the Jessica AI product (Telegram chat UI +
  LLM + the non-AI logistics work underneath).
- Help FIL negotiate fair compensation with his employer.
- Build out internal tooling that compounds (fuel optimizer is the
  first — pricing-driven decisions, route planning). Add tools as
  needs surface.

## Next

(concrete, near-term)

(empty — see HANDOFF "Current state" for what's actually built and
what's queued for the per-repo session)

## From meta

(meta-session writes here; the per-repo Claude reads it at
SessionStart for direction)

- **2026-05-19 — `scattermind/meta/templates/gh-pages/` exists.**
  Whitelist-style static-`<PUBLISH_DIR>` deploy template for new
  repos. Jessica-ai-project's existing **allowlist via
  `scripts/build-dist.sh`** (shipped 2026-05-18, PRs #4-#5) is a
  shell-script variant of the same idea — instead of a static
  `<PUBLISH_DIR>` the build script enumerates `cp` lines for each
  publishable file. Functionally equivalent guardrail; the meta
  template's README treats jessica-ai-project alongside daedalus
  and blinker as "real-world variants to copy from" for new repos
  that need build-time allowlist filtering. **No action required**:
  jessica-ai-project keeps its current pattern.

## For meta

(the per-repo Claude writes here when there's something meta
should know — meta reads at its next multi-repo session start)

(empty)
