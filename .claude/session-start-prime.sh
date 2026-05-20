#!/usr/bin/env bash
# Canonical SessionStart prime for single-repo ScatterMind sessions.
#
# BYTE-IDENTICAL across every ScatterMind repo. This file and
# .claude/settings.json are the two canonical-mirrored files: edit in
# scattermind/meta first, then propagate byte-for-byte. Never edit in isolation
# (see meta HANDOFF "Standard project repo structure" + "Compaction & priming").
#
# Why a head-slice and not a whole-file cat: the harness caps how much
# SessionStart additionalContext it injects inline (~25K tokens; observed
# <~58.7KB for dense HANDOFF content). A whole-file cat of a large HANDOFF blows
# the cap, so the harness files the blob and shows the model only a ~2KB preview
# -> README/VISION/FUTURE + the cross-Claude inbox never surface. HANDOFF.md is
# newest-first, so its HEAD == current state; older history/architecture is read
# on demand. The ## From meta inbox is pulled out explicitly because it lives
# below the slice. See meta HANDOFF for the resume-block authoring protocol.
set -u

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true

input=$(cat 2>/dev/null || true)
src=$(printf '%s' "$input" | jq -r '.source // ""' 2>/dev/null || echo "")

SLICE=12000

hs=""; fm=""
if [ -f HANDOFF.md ]; then
  hs=$(head -c "$SLICE" HANDOFF.md)
  # Drop a possibly-broken trailing UTF-8 char from the byte-cut (keep raw if iconv missing).
  hs=$(printf '%s' "$hs" | iconv -f UTF-8 -t UTF-8 -c 2>/dev/null || printf '%s' "$hs")
  hsz=$(wc -c < HANDOFF.md | tr -d ' ')
  # Only pull ## From/For meta out separately when the slice didn't already
  # cover the whole file (small repos: head -c already includes it -> avoid dup).
  if [ "${hsz:-0}" -gt "$SLICE" ]; then
    fm=$(awk '/^## (From|For) meta[[:space:]]*$/{p=1} /^## /&&!/^## (From|For) meta[[:space:]]*$/{p=0} p' HANDOFF.md)
  fi
fi
fut=""; [ -f FUTURE.md ] && fut=$(cat FUTURE.md)
vis=""; [ -f VISION.md ] && vis=$(cat VISION.md)

ctx=$(
  printf '=== Repo priming (HEAD-slice; auto-injected by SessionStart) ===\n'
  printf 'This is a bounded HEAD slice of HANDOFF.md, not the whole file. If you can see the From/For meta + FUTURE + VISION sections below, priming fit inline. If you are seeing only a ~2KB preview, the blob was truncated: Read HANDOFF.md in full (chunk it, >25K tokens) + FUTURE.md + the ## From meta section before working.\n'
  printf 'Soft behaviors (not hook-enforced): announce a PR merge in chat before triggering it (the Allow/Deny prompt is per-call); use judgement on whether HANDOFF.md / README.md need updating after a non-trivial change.\n\n'
  printf -- '--- HANDOFF.md (HEAD slice — newest-first = current state; resume block is at the very top) ---\n'
  printf '%s\n' "$hs"
  if [ -n "$fm" ]; then
    printf -- '\n--- From/For meta (cross-Claude channels — act on ## From meta) ---\n'
    printf '%s\n' "$fm"
  fi
  if [ -n "$fut" ]; then
    printf -- '\n--- FUTURE.md (backlog) ---\n'
    printf '%s\n' "$fut"
  fi
  if [ -n "$vis" ]; then
    printf -- '\n--- VISION.md (intent) ---\n'
    printf '%s\n' "$vis"
  fi
  printf -- '\nNOTE: HANDOFF.md above is only the HEAD slice. Read it in full (chunked) for older history/architecture + the complete ## From meta / ## For meta channels before substantive work. README.md on demand.\n'
)

# Instrumentation: surface the resolved source + assembled blob size so a future
# session can confirm (a) whether source=='compact' fires after a compaction and
# (b) that the blob stays under the injection cap. Remove once both are settled.
bsz=$(printf '%s' "$ctx" | wc -c | tr -d ' ')
ctx="$ctx
[prime-diag: source='${src}' blob=${bsz}B slice=${SLICE}B]"

if [ "$src" = "compact" ]; then
  ctx="$ctx

=== Resumed after COMPACTION (you have the summary in context + a live turn) ===
Write a fresh checkpoint to the TOP of HANDOFF.md: overwrite the resume block with current state (branch; in-flight work or 'resume cleanly'; open ## From meta items), commit + push. Then tell the user: HANDOFF updated post-compaction — /clear for a fresh session, or continue."
fi

jq -nc --arg ctx "$ctx" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'
