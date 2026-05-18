"""
Run the gas-price optimizer on the built-in Brampton-originated routes.

Usage:
    python -m fuel_optimizer                       # all routes, text out
    python -m fuel_optimizer --route 4             # just route #4 (1-indexed)
    python -m fuel_optimizer --markdown            # markdown output
    python -m fuel_optimizer --mpg 6 --tank 250    # custom truck
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from .corpus import PilotSite, load_pilot_sites
from .geo import CityDB, Coords, haversine
from .optimize import Plan, Station, optimize
from .routes import ROUTES, RouteSpec

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRICES = REPO_ROOT / "corpus" / "pilot-flying-j" / "2026-05-17" / "cp149834.xls"
DEFAULT_CITIES = REPO_ROOT / "corpus" / "geo" / "us_cities.csv"


def find_on_route_stations(
    origin: Coords,
    dest: Coords,
    sites: list[PilotSite],
    citydb: CityDB,
    max_detour_mi: float = 50.0,
) -> tuple[list[Station], int]:
    """Return on-route stations + count of sites we couldn't geocode."""
    direct = haversine(origin, dest)
    stations: list[Station] = []
    ungeocoded = 0
    for site in sites:
        coords = citydb.lookup(site.city, site.state)
        if coords is None:
            ungeocoded += 1
            continue
        d_origin = haversine(origin, coords)
        d_dest = haversine(coords, dest)
        detour = (d_origin + d_dest) - direct
        if detour <= max_detour_mi:
            stations.append(
                Station(
                    name=f"#{site.site_code} {site.city}, {site.state}",
                    miles=d_origin,
                    price=site.your_price,
                )
            )
    return stations, ungeocoded


def format_text(
    spec: RouteSpec,
    direct_mi: float,
    candidate_count: int,
    ungeocoded: int,
    tank_gallons: float,
    mpg: float,
    plan: Plan,
    out: TextIO,
) -> None:
    tank_miles = tank_gallons * mpg
    print(f"== {spec.name} ==", file=out)
    print(f"  {spec.origin[0]}, {spec.origin[1]} → "
          f"{spec.destination[0]}, {spec.destination[1]}", file=out)
    print(f"  Great-circle distance: {direct_mi:.0f} mi", file=out)
    print(f"  Pilot sites on route (≤50 mi detour): {candidate_count}"
          f"  (skipped {ungeocoded} ungeocoded sites globally)", file=out)
    print(f"  Truck: tank {tank_gallons:.0f} gal × {mpg:.1f} mpg "
          f"= {tank_miles:.0f} mi range", file=out)
    if spec.note:
        print(f"  Note: {spec.note}", file=out)
    print(file=out)

    if not plan.feasible:
        print(f"  INFEASIBLE: {plan.error}", file=out)
        print(file=out)
        return

    if not plan.stops:
        print("  No fuel stops needed — destination within starting-tank range.",
              file=out)
    else:
        print(f"  {'Mile':>6}  {'Stop':<38} {'Gal':>7}  {'$/gal':>7}  {'Cost':>9}",
              file=out)
        for s in plan.stops:
            print(f"  {s.station.miles:>6.0f}  {s.station.name:<38} "
                  f"{s.gallons:>7.1f}  ${s.station.price:>6.3f}  "
                  f"${s.cost:>8.2f}", file=out)
        print(f"  {'':6}  {'':38} {plan.total_gallons:>7.1f}            "
              f"${plan.total_cost:>8.2f}", file=out)
    print(f"  Arrival fuel: ~{plan.arrival_fuel_gallons:.0f} gal", file=out)
    print(file=out)


def format_markdown(
    spec: RouteSpec,
    direct_mi: float,
    candidate_count: int,
    ungeocoded: int,
    tank_gallons: float,
    mpg: float,
    plan: Plan,
    out: TextIO,
) -> None:
    tank_miles = tank_gallons * mpg
    print(f"### {spec.name}\n", file=out)
    print(f"- **Origin → Destination:** {spec.origin[0]}, {spec.origin[1]} → "
          f"{spec.destination[0]}, {spec.destination[1]}", file=out)
    print(f"- **Great-circle distance:** {direct_mi:.0f} mi", file=out)
    print(f"- **Pilot sites on route:** {candidate_count} (≤50 mi detour; "
          f"{ungeocoded} ungeocoded globally)", file=out)
    print(f"- **Truck:** tank {tank_gallons:.0f} gal × {mpg:.1f} mpg "
          f"= {tank_miles:.0f} mi range", file=out)
    if spec.note:
        print(f"- *Note:* {spec.note}", file=out)
    print(file=out)

    if not plan.feasible:
        print(f"> **INFEASIBLE:** {plan.error}\n", file=out)
        return

    if not plan.stops:
        print("_No fuel stops needed — destination within starting-tank range._\n",
              file=out)
    else:
        print("| Mile | Stop | Gal | $/gal | Cost |", file=out)
        print("|-----:|:-----|----:|------:|-----:|", file=out)
        for s in plan.stops:
            print(f"| {s.station.miles:.0f} | {s.station.name} | "
                  f"{s.gallons:.1f} | ${s.station.price:.3f} | "
                  f"${s.cost:.2f} |", file=out)
        print(f"| | **Total** | **{plan.total_gallons:.1f}** | | "
              f"**${plan.total_cost:.2f}** |\n", file=out)
    print(f"_Arrival fuel: ~{plan.arrival_fuel_gallons:.0f} gal._\n", file=out)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--route", type=int, default=None,
                   help="run only route N (1-indexed)")
    p.add_argument("--markdown", action="store_true",
                   help="markdown output")
    p.add_argument("--tank", type=float, default=200.0,
                   help="tank capacity in gallons (default 200)")
    p.add_argument("--mpg", type=float, default=6.5,
                   help="fuel economy (default 6.5)")
    p.add_argument("--start-gallons", type=float, default=None,
                   help="starting fuel in gallons (default: full tank)")
    p.add_argument("--reserve", type=float, default=20.0,
                   help="reserve gallons at destination (default 20)")
    p.add_argument("--detour", type=float, default=50.0,
                   help="max on-route detour in miles (default 50)")
    p.add_argument("--prices", type=Path, default=DEFAULT_PRICES,
                   help="path to Pilot pricing XLS")
    p.add_argument("--cities", type=Path, default=DEFAULT_CITIES,
                   help="path to US cities CSV")
    args = p.parse_args(argv)

    citydb = CityDB(args.cities)
    sites = load_pilot_sites(args.prices)

    selected = ROUTES if args.route is None else [ROUTES[args.route - 1]]
    fmt = format_markdown if args.markdown else format_text
    out = sys.stdout

    if args.markdown:
        print("# Gas-price-optimized fueling plans\n", file=out)
        print(f"Pilot prices: `{args.prices.name}` "
              f"(account 149834 — KJS Transport Inc.)\n", file=out)
        print(f"Truck assumed: {args.tank:.0f} gal tank · {args.mpg:.1f} mpg "
              f"· starting "
              f"{'full' if args.start_gallons is None else f'{args.start_gallons:.0f} gal'}"
              f" · {args.reserve:.0f} gal reserve at destination.\n", file=out)
        print("Optimizer: greedy look-ahead (Khuller, Malekian & Mestre 2007); "
              "optimal under continuous fueling, on-route stations only, "
              "constant mpg.\n", file=out)

    for spec in selected:
        origin_coords = citydb.lookup(*spec.origin)
        dest_coords = citydb.lookup(*spec.destination)
        if origin_coords is None or dest_coords is None:
            print(f"!! Could not geocode {spec.name}: "
                  f"origin={origin_coords}, dest={dest_coords}", file=sys.stderr)
            continue

        direct = haversine(origin_coords, dest_coords)
        stations, ungeocoded = find_on_route_stations(
            origin_coords, dest_coords, sites, citydb, args.detour,
        )

        plan = optimize(
            total_miles=direct,
            stations=stations,
            tank_gallons=args.tank,
            mpg=args.mpg,
            start_gallons=args.start_gallons,
            reserve_gallons=args.reserve,
        )

        fmt(spec, direct, len(stations), ungeocoded,
            args.tank, args.mpg, plan, out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
