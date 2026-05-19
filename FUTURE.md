# Future

Forward-looking notes for jessica-ai-project. Vague goals and queued
work.

This is the **human-facing** roadmap; HANDOFF.md is the AI's
internal notebook. Some redundancy between them is fine.

## How this file works

- Anyone (you, this repo's per-repo Claude, the meta-session Claude)
  can append. Mark ownership inline when it matters: `[ME]` /
  `[AI]` / `[HYBRID]`.
- Status tags are **optional** — use only when status meaningfully
  differs from "not started." Five values:
    - `[TODO]` — not started (implicit; omit the tag)
    - `[PARTIAL]` — partially implemented; more work needed
    - `[QA-PENDING]` — code shipped; awaiting human QA before done
    - `[BLOCKED]` — waiting on something external (body explains)
    - _(implicit done = moved to `## Archive`, no tag)_
  Status tag goes after the ownership tag, each backtick-wrapped:
  `` `[AI] [QA-PENDING]` ``. Vague aspirational items typically
  have no tags — they're just "things we eventually want."
- When work happens, record it in HANDOFF.md. If the entry is now
  ME-confirmed done, move it under `## Archive` with a one-line
  ship note. If partially shipped, update the status tag (and
  prose if useful). Bias toward keeping `## Backlog` focused.
- No cross-Claude channels here. Those live in HANDOFF.md
  (`## From meta` / `## For meta` sections) — AI-to-AI plumbing
  belongs in the AI-first file.

## Backlog

(everything queued: concrete shapeable work and vague aspirations
mixed; tags clarify shape when it matters. See HANDOFF "Current
state" for what's actually built and what's queued for the per-repo
session.)

- **Help FIL succeed on the Jessica AI product** — Telegram chat UI +
  LLM + the non-AI logistics work underneath.
- **Help FIL negotiate fair compensation** — with his employer.
- **Build out internal tooling that compounds** — fuel optimizer is
  the first (pricing-driven decisions, route planning). Add tools
  as needs surface.

## Archive

_Completed items move here from `## Backlog` once ME-confirmed.
Newest on top. Keep entries indefinitely — pruning is a manual
call by ME when the section gets too long._

(empty)
