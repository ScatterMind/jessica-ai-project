# Route-planner passcode

The encrypted bundle at `site/route-planner/data.enc.json` is locked
with this passcode. Decryption happens in the browser via Web Crypto
(PBKDF2-SHA-256 200k → AES-GCM-256).

## Current passcode

    ii8h-twv1-go0n

## Where it does and doesn't live

- This file (`notes/route-planner-passcode.md`) — **private**, lives
  in the private repo only. `notes/` does not deploy.
- The deployed bundle (`site/route-planner/data.enc.json`) — public,
  but contains only the AES-GCM ciphertext + salt + IV. Useless
  without the passcode.
- `site/` is the only directory that deploys to gh-pages
  (`publish_dir: ./site` in `.github/workflows/deploy-main.yml`), so
  anything outside `site/` — including this file — never reaches the
  public web.

If `notes/` ever becomes shared / multi-contributor: move the passcode
to an out-of-repo secret (password manager, Actions secret, …) and
strip it from git history.

## How to rotate

```bash
PYTHONPATH=src python3 -m fuel_optimizer.web_build --passcode <new-passcode>
```

That rewrites `site/route-planner/data.enc.json` (and refreshes the
cities CSV copy). Commit both files, then update the passcode above
and commit this file. Anyone holding the old passcode loses access on
the next deploy.

To generate a fresh random passcode and have the script print it,
omit `--passcode`:

```bash
PYTHONPATH=src python3 -m fuel_optimizer.web_build
```

The 12-character alphanumeric format (`xxxx-xxxx-xxxx`) gives ~71 bits
of entropy — at 200k PBKDF2 iterations, brute-force is infeasible for
any realistic attacker.
