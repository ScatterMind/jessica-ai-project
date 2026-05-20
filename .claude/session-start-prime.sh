#!/usr/bin/env bash
# Canonical SessionStart prime for single-repo ScatterMind sessions.
#
# BYTE-IDENTICAL across every ScatterMind repo (alongside .claude/settings.json).
# Edit in scattermind/meta first, then mirror byte-for-byte. Never edit in
# isolation. See meta HANDOFF "## Compaction & priming (head-slice model)".
#
# Design (confirmed 2026-05-20 by a live daedalus reset): the SessionStart
# additionalContext injection cap is a LOW byte threshold (<~24KB observed —
# NOT the ~25K-token / ~100KB once assumed). A blob over it is persisted to a
# file and the model sees only a ~2KB preview. So this prime FRONT-LOADS the
# must-haves into the first ~2KB — the diag, a truncation/recovery note, the
# post-compaction instruction, then the resume block — so they survive even
# when the rest is cut; and it keeps the remainder small (bounded head slice +
# the ## From meta inbox only, no FUTURE/For-meta) so it also has a real chance
# of fitting inline. The resume block at the top of HANDOFF is load-bearing.
set -u

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || true

input=$(cat 2>/dev/null || true)
src=$(printf '%s' "$input" | jq -r '.source // ""' 2>/dev/null || echo "")

SLICE=6000   # HANDOFF head bytes (resume block + the newest few entries)
FMCAP=3000   # ## From meta inbox cap

hs=""; fm=""
if [ -f HANDOFF.md ]; then
  hs=$(head -c "$SLICE" HANDOFF.md)
  hs=$(printf '%s' "$hs" | iconv -f UTF-8 -t UTF-8 -c 2>/dev/null || printf '%s' "$hs")
  hsz=$(wc -c < HANDOFF.md | tr -d ' ')
  if [ "${hsz:-0}" -gt "$SLICE" ] && ! printf '%s' "$hs" | grep -qE '^## From meta[[:space:]]*$'; then
    # Extract the ## From meta inbox only when it sits BELOW the slice (newest-
    # first HANDOFFs, e.g. daedalus). If the slice already contains it (shorter
    # HANDOFFs with channels high up, e.g. blinker), don't duplicate it. The
    # session's own ## For meta outbox isn't needed at startup either way.
    fm=$(awk '/^## From meta[[:space:]]*$/{p=1} /^## /&&!/^## From meta[[:space:]]*$/{p=0} p' HANDOFF.md)
    fmfull=$(printf '%s' "$fm" | wc -c | tr -d ' ')
    if [ "${fmfull:-0}" -gt "$FMCAP" ]; then
      fm=$(printf '%s' "$fm" | head -c "$FMCAP" | iconv -f UTF-8 -t UTF-8 -c 2>/dev/null || printf '%s' "$fm" | head -c "$FMCAP")
      fm="$fm
[## From meta truncated to ${FMCAP}B — read HANDOFF.md for the rest]"
    fi
  fi
fi
vis=""; [ -f VISION.md ] && vis=$(cat VISION.md)

body=$(
  printf 'PRIMING TRUNCATES to a ~2KB preview when over the injection cap (a low byte limit). If the sections below (## From meta / VISION) are missing or the text is cut, you got the preview — Read HANDOFF.md in full (chunk it; >25K tokens, a single Read errors) + FUTURE.md + the ## From meta section before working. The resume block just below is the curated current state.\n'
  if [ "$src" = "compact" ]; then
    printf '\nRESUMED AFTER COMPACTION — you have the summary in context + a live turn. Write a fresh checkpoint to the TOP of HANDOFF.md (overwrite the resume block with current state; commit + push), then tell the user: HANDOFF updated post-compaction — /clear for a fresh session, or continue.\n'
  fi
  printf -- '\n--- HANDOFF.md (HEAD slice — newest-first; resume block is first) ---\n'
  printf '%s\n' "$hs"
  if [ -n "$fm" ]; then
    printf -- '\n--- ## From meta (cross-Claude inbox — act on these) ---\n'
    printf '%s\n' "$fm"
  fi
  if [ -n "$vis" ]; then
    printf -- '\n--- VISION.md ---\n'
    printf '%s\n' "$vis"
  fi
  printf -- '\nThis is a head slice — Read HANDOFF.md in full + FUTURE.md on demand. Soft behaviors: announce a PR merge in chat before triggering it (Allow/Deny is per-call); use judgement on HANDOFF.md / README.md updates after a non-trivial change.\n'
)

# Diag FIRST so the blob size is visible even when truncated to a ~2KB preview.
bsz=$(printf '%s' "$body" | wc -c | tr -d ' ')
ctx="[prime-diag: source='${src}' blob≈${bsz}B slice=${SLICE}B — if this line + a ~2KB preview is all you see, the blob truncated and only items in the first ~2KB reached you]
$body"

jq -nc --arg ctx "$ctx" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'
