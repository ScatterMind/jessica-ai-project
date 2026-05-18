"""Built-in sample routes (all originating in Brampton, ON)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteSpec:
    name: str
    origin: tuple[str, str]
    destination: tuple[str, str]
    note: str = ""


ROUTES: list[RouteSpec] = [
    # Brampton-involving (KJS terminal is in Brampton)
    RouteSpec(
        "Brampton → Detroit",
        ("Brampton", "ON"),
        ("Detroit", "MI"),
        "Short cross-border haul out of home terminal.",
    ),
    RouteSpec(
        "Brampton → Atlanta",
        ("Brampton", "ON"),
        ("Atlanta", "GA"),
        "Southeast long-haul out of home terminal.",
    ),
    RouteSpec(
        "Atlanta → Brampton",
        ("Atlanta", "GA"),
        ("Brampton", "ON"),
        "Northbound return to home terminal.",
    ),
    # Intercity US-US (typical pickup → delivery legs)
    RouteSpec(
        "Chicago → Dallas",
        ("Chicago", "IL"),
        ("Dallas", "TX"),
        "Midwest → south-central intercity haul.",
    ),
    RouteSpec(
        "Los Angeles → Atlanta",
        ("Los Angeles", "CA"),
        ("Atlanta", "GA"),
        "Transcontinental west-to-southeast.",
    ),
    RouteSpec(
        "Seattle → Phoenix",
        ("Seattle", "WA"),
        ("Phoenix", "AZ"),
        "Pacific-NW → southwest.",
    ),
    RouteSpec(
        "Miami → New York",
        ("Miami", "FL"),
        ("New York", "NY"),
        "East-coast northbound.",
    ),
]
