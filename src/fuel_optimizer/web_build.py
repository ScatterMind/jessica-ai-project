"""
Build the encrypted station dataset that the public route-planner UI consumes.

Reads:
  corpus/pilot-flying-j/<date>/cp149834.xls   (prices)
  corpus/geo/us_cities.csv                    (coords)

Writes:
  site/route-planner/data.enc.json            (AES-GCM-encrypted bundle)

The output is a JSON envelope:
  {
    "version": 1,
    "snapshot": "2026-05-17",
    "kdf": "PBKDF2-HMAC-SHA256",
    "iterations": 200000,
    "salt":  base64,                # 16 bytes
    "iv":    base64,                # 12 bytes
    "cipher": "AES-GCM",
    "ciphertext": base64,           # ct || 16-byte tag
  }

Plaintext payload (post-decrypt) is:
  {
    "snapshot": str,
    "account":  str,
    "stations": [
      { "site": "001", "city": "...", "st": "PA", "lat": ..., "lon": ...,
        "price": 5.484, "retail": 6.059 },
      ...
    ],
  }

Both AES-GCM (pycryptodome here, Web Crypto in the browser) layer the
auth tag onto the end of the ciphertext, so this round-trips byte-for-byte
with SubtleCrypto.decrypt on the client.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import shutil
import string
import sys
from pathlib import Path

from Crypto.Cipher import AES

from .corpus import load_pilot_sites
from .geo import CityDB

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRICES = REPO_ROOT / "corpus" / "pilot-flying-j" / "2026-05-17" / "cp149834.xls"
DEFAULT_CITIES = REPO_ROOT / "corpus" / "geo" / "us_cities.csv"
DEFAULT_OUT = REPO_ROOT / "site" / "route-planner" / "data.enc.json"
DEFAULT_CITIES_OUT = REPO_ROOT / "site" / "route-planner" / "cities.csv"
ITERATIONS = 200_000


def generate_passcode() -> str:
    """12-char URL-safe alphanumeric. ~71 bits of entropy."""
    alphabet = string.ascii_lowercase + string.digits
    return "-".join(
        "".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3)
    )


def build_plaintext(prices_path: Path, cities_path: Path, snapshot: str) -> bytes:
    citydb = CityDB(cities_path)
    sites = load_pilot_sites(prices_path)
    stations = []
    skipped = 0
    for s in sites:
        c = citydb.lookup(s.city, s.state)
        if c is None:
            skipped += 1
            continue
        stations.append({
            "site":   s.site_code,
            "city":   s.city,
            "st":     s.state,
            "lat":    round(c.lat, 5),
            "lon":    round(c.lon, 5),
            "price":  round(s.your_price, 4),
            "retail": round(s.retail_price, 4),
        })
    print(f"Geocoded {len(stations)} of {len(sites)} sites "
          f"(skipped {skipped}).", file=sys.stderr)

    payload = {
        "snapshot": snapshot,
        "account":  "149834",
        "stations": stations,
    }
    return json.dumps(payload, separators=(",", ":")).encode()


def encrypt(plaintext: bytes, passcode: str) -> dict:
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = hashlib.pbkdf2_hmac("sha256", passcode.encode(), salt, ITERATIONS, dklen=32)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    return {
        "version":    1,
        "kdf":        "PBKDF2-HMAC-SHA256",
        "iterations": ITERATIONS,
        "salt":       base64.b64encode(salt).decode(),
        "iv":         base64.b64encode(iv).decode(),
        "cipher":     "AES-GCM",
        "ciphertext": base64.b64encode(ct + tag).decode(),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prices", type=Path, default=DEFAULT_PRICES)
    p.add_argument("--cities", type=Path, default=DEFAULT_CITIES)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--passcode", default=None,
                   help="passcode for AES-GCM key derivation. "
                        "If omitted, a random one is generated and printed.")
    p.add_argument("--snapshot", default="2026-05-17",
                   help="label embedded in the plaintext payload.")
    args = p.parse_args(argv)

    passcode = args.passcode or generate_passcode()
    plaintext = build_plaintext(args.prices, args.cities, args.snapshot)
    envelope = encrypt(plaintext, passcode)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(envelope, indent=2) + "\n")

    # Copy the public cities CSV into the deployed route-planner so the
    # browser can geocode user-typed origins/destinations.
    shutil.copyfile(args.cities, DEFAULT_CITIES_OUT)

    print(f"\nWrote {args.out.relative_to(REPO_ROOT)} "
          f"({args.out.stat().st_size:,} bytes).", file=sys.stderr)
    print(f"Copied {args.cities.relative_to(REPO_ROOT)} → "
          f"{DEFAULT_CITIES_OUT.relative_to(REPO_ROOT)} "
          f"({DEFAULT_CITIES_OUT.stat().st_size:,} bytes).", file=sys.stderr)
    print(f"Plaintext size: {len(plaintext):,} bytes.", file=sys.stderr)
    if args.passcode is None:
        print(f"\n  PASSCODE:  {passcode}\n", file=sys.stderr)
        print("  Save this in a password manager. It is NOT stored in the",
              file=sys.stderr)
        print("  repo. To rotate, re-run this script with --passcode <new>.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
