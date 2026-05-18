# fuel_optimizer

Gas-price-optimal refueling planner. Given a route A→B and a set of
on-route Pilot Flying J stations with prices, computes a fueling plan
(which stations to stop at, how much to buy at each) that minimizes
total fuel cost.

Built for KJS Transport (home terminal: Brampton, ON) but the optimizer
itself is route-agnostic — works on any A→B haul.

## Quick start

```bash
# All built-in sample routes, default truck (200 gal, 6.5 mpg, full start)
PYTHONPATH=src python3 -m fuel_optimizer

# Markdown output
PYTHONPATH=src python3 -m fuel_optimizer --markdown

# One route, custom truck
PYTHONPATH=src python3 -m fuel_optimizer --route 5 --tank 200 --mpg 6.0

# Force refueling decisions by starting near-empty
PYTHONPATH=src python3 -m fuel_optimizer --start-gallons 50
```

See `python3 -m fuel_optimizer --help` for all flags.

## Algorithm

Greedy look-ahead, after Khuller, Malekian & Mestre (2007), *To fill or
not to fill: the gas station problem*. At each station, look ahead
within tank range:

- If a cheaper station is reachable, buy just enough to reach it.
- Otherwise, fill the tank (or top up for destination + reserve,
  whichever is less).

Provably optimal under: continuous fueling (any gallon amount),
on-route stations only (no detour cost), constant mpg, single fuel
type.

## Modules

| File | Role |
|------|------|
| `optimize.py` | Pure algorithm. Takes a list of `Station(name, miles, price)` and returns a `Plan` with stops, total cost, arrival fuel. No I/O. |
| `corpus.py`   | Loads Pilot prices from the XLS in `corpus/pilot-flying-j/<date>/`. Returns `PilotSite` records. |
| `geo.py`      | Haversine + a `CityDB` that resolves `(city, state)` → coords using `corpus/geo/us_cities.csv`. Hard-coded entries for Brampton + ~17 small Pilot hamlets the CSV doesn't list. |
| `routes.py`   | The built-in sample route set. Mix of Brampton-involving (terminal) and US-US intercity. |
| `cli.py`      | Glues it together: resolves origin/destination, filters on-route stations (≤50 mi detour by default), runs `optimize`, prints text or markdown. |

## Adding a new route

Append to `ROUTES` in `routes.py`:

```python
RouteSpec("Memphis → Phoenix", ("Memphis", "TN"), ("Phoenix", "AZ"),
         "Optional note.")
```

The optimizer will pick up any Pilot site within `--detour` miles of the
great-circle line between the two endpoints.

## Modeling caveats

The greedy is exact for the abstract gas-station problem, but a few
real-world frictions are approximated:

- **Great-circle distance** as the route length, not actual driving
  miles. Real driving distance is typically 1.1–1.2× greater, so plans
  underestimate fuel needed. Multiply `--tank` down (or override
  `--start-gallons`) to compensate.
- **No road graph.** A site is "on route" if the great-circle detour
  through it stays within `--detour` miles. Lake crossings (e.g., a
  literal Brampton → Chicago straight line crosses Lake Huron) aren't
  modeled — the sites picked are still all on-land Pilot locations, but
  the mile markers can be slightly off for routes where actual highways
  loop around water.
- **Mile-marker proxy.** A site's position along the route is taken as
  its great-circle distance from origin, which is exact only if the
  site is *on* the line. For near-line sites (within 50 mi), the error
  is small relative to tank range.
- **No hours-of-service / driver constraints.** The optimizer picks
  whichever stops are cheapest; doesn't try to align with mandatory
  10-hour rests, weigh stations, etc.
- **Single fuel type (DSL).** The corpus is diesel-only.

These approximations are fine for a planning tool that informs
where-to-fuel decisions; they would not be fine if the plan were
auto-executed by a routing system.

## Data dependencies

- `corpus/pilot-flying-j/<date>/cp149834.xls` — vendor pricing (private).
- `corpus/geo/us_cities.csv` — public city geocoding data.

Both paths are resolved relative to the repo root; override with
`--prices` and `--cities`.
