#!/usr/bin/env bash
# Build the deployable bundle by ALLOWLIST.
#
# Both deploy-main.yml and deploy-dev.yml call this script to construct
# ./dist from a hand-maintained list of files under site/. Files in
# site/ that don't appear below are NOT published — even if they're
# checked into the repo, even if they're sitting right next to allowed
# files. This is the safety net against accidentally publishing
# README.md / internal notes / proprietary data dropped under site/.
#
# To add a new public file: add a `cp` line below it and commit.
# To remove one: delete the line and commit; next deploy overwrites
# (deploy-main uses keep_files: true; the gh-pages root file remains
# until manually removed there).

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

rm -rf dist
mkdir -p dist/route-planner

# ---- Allowlist ----
cp site/index.html                       dist/
cp site/banner.svg                       dist/
cp site/route-planner/index.html         dist/route-planner/
cp site/route-planner/app.js             dist/route-planner/
cp site/route-planner/style.css          dist/route-planner/
cp site/route-planner/data.enc.json      dist/route-planner/
cp site/route-planner/cities.csv         dist/route-planner/
# Intentionally excluded:
#   site/route-planner/README.md  — internal architecture docs
# -------------------

echo
echo "Files deployed:"
( cd dist && find . -type f | sort | sed 's|^\./|  |' )

echo
echo "Files in site/ NOT deployed (deliberately, by allowlist):"
missed=0
while IFS= read -r f; do
  rel="${f#site/}"
  if [ ! -f "dist/$rel" ]; then
    echo "  site/$rel"
    missed=$((missed + 1))
  fi
done < <(find site -type f | sort)
if [ "$missed" -eq 0 ]; then
  echo "  (none)"
fi
