"""Geographic helpers: great-circle distance, city geocoding."""
from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

EARTH_RADIUS_MI = 3958.8

# Points not in corpus/geo/us_cities.csv (Canadian origin + a handful of
# small Pilot-truck-stop hamlets the CSV doesn't list). Hand-coded only
# where the city is plausibly on a sample route.
HARDCODED: dict[tuple[str, str], tuple[float, float]] = {
    ("Brampton", "ON"):       (43.7315, -79.7624),
    ("Berkshire", "OH"):      (40.3640, -82.9410),
    ("Carmel Church", "VA"):  (37.9700, -77.4200),
    ("Carneys Point", "NJ"):  (39.7100, -75.4600),
    ("Cinnaminson", "NJ"):    (40.0000, -74.9600),
    ("Dubois", "PA"):         (41.1200, -78.7600),
    ("Fort Chiswell", "VA"):  (36.9300, -80.9500),
    ("Frystown", "PA"):       (40.4600, -76.4000),
    ("Jedburg", "SC"):        (33.0200, -80.1600),
    ("Jurupa Valley", "CA"):  (33.9900, -117.4900),
    ("Kimball Township", "MI"):(42.9500, -82.5500),
    ("Lake Township", "OH"):  (40.9400, -81.4200),
    ("Port Wentworth", "GA"): (32.1500, -81.1600),
    ("Rocker", "MT"):         (46.0000, -112.5900),
    ("Saint Lucie", "FL"):    (27.2700, -80.3600),
    ("Woodhaven", "MI"):      (42.1300, -83.2400),
    ("Desert Springs", "AZ"): (33.8500, -112.1300),
    ("Pembroke", "NY"):       (43.0500, -78.4100),
}


@dataclass(frozen=True)
class Coords:
    lat: float
    lon: float


def haversine(a: Coords, b: Coords) -> float:
    """Great-circle distance in miles."""
    p1, p2 = math.radians(a.lat), math.radians(b.lat)
    dp = math.radians(b.lat - a.lat)
    dl = math.radians(b.lon - a.lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(h))


def _candidates(name: str) -> list[str]:
    """Generate normalization candidates for a city name."""
    out = [name]
    sub_pairs = (
        (r"^St\.?\s+", "Saint "),
        (r"^Mt\.?\s+", "Mount "),
        (r"^Ft\.?\s+", "Fort "),
        (r"\bEast St\.?\s+", "East Saint "),
        (r"\bWest St\.?\s+", "West Saint "),
    )
    for pat, repl in sub_pairs:
        n = re.sub(pat, repl, name, flags=re.IGNORECASE)
        if n != name:
            out.append(n)
    out.append(name.replace("-", " "))
    out.append(name.replace(".", ""))
    return out


class CityDB:
    """Loads us_cities.csv once and resolves (city, state) → Coords."""

    def __init__(self, csv_path: Path):
        self._exact: dict[tuple[str, str], Coords] = {}
        with open(csv_path, newline="") as f:
            for row in csv.DictReader(f):
                key = (row["CITY"], row["STATE_CODE"])
                self._exact[key] = Coords(
                    float(row["LATITUDE"]), float(row["LONGITUDE"])
                )

    @lru_cache(maxsize=4096)
    def lookup(self, city: str, state: str) -> Optional[Coords]:
        if (city, state) in HARDCODED:
            lat, lon = HARDCODED[(city, state)]
            return Coords(lat, lon)
        for cand in _candidates(city):
            hit = self._exact.get((cand, state))
            if hit:
                return hit
        return None
