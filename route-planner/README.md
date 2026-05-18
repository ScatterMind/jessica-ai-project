# Route planner

Static web app that takes an origin + destination, asks
[OSRM](https://project-osrm.org/) for a real driving route, matches Pilot
Flying J stations to the route polyline, and runs the
[`fuel_optimizer`](../../src/fuel_optimizer/) greedy on them. Renders
the result on a Leaflet/OSM map with all on-route stations color-graded
by price and the optimal-stop subset highlighted.

This folder is part of `site/` so it deploys with the rest of the public
site to `https://scattermind.github.io/jessica-ai-project/route-planner/`.

## Why passcode-gated

The station list + Pilot prices are vendor-confidential. They ship as
an AES-GCM-encrypted blob (`data.enc.json`); the page asks for a
passcode, derives a key with PBKDF2-SHA-256 / 200k iterations, and
decrypts in the browser via Web Crypto. Without the passcode the blob
is unreadable.

Strength: brute-forcing a 12-char alphanumeric (~71 bits of entropy) at
200k PBKDF2 iterations is computationally infeasible for any realistic
attacker. The repo is also private, so the encrypted blob is doubly
gated until the site is published.

The passcode is **not** stored in the repo. Whoever runs
`web_build.py` is told the passcode once, on stderr, and is responsible
for saving it (password manager) and sharing it with whoever needs it.

## Files

| File | Purpose |
|------|---------|
| `index.html`     | Passcode prompt + main UI shell. |
| `app.js`         | Crypto, geocoding, OSRM client, optimizer port, Leaflet rendering, turn-by-turn formatter. ~360 lines, no build step. |
| `style.css`      | Dark theme matching `site/banner.svg`. |
| `data.enc.json`  | AES-GCM-encrypted bundle: snapshot date, account, full station list with coords + your-price + retail. Generated. |
| `cities.csv`     | Public US-cities geocoding table for user-typed origin/destination. Generated (copied from `corpus/geo/`). |

## Rebuild

Both generated files come from `src/fuel_optimizer/web_build.py`:

```bash
# Re-encrypt with a fresh random passcode (printed to stderr):
PYTHONPATH=src python3 -m fuel_optimizer.web_build

# Or rotate to a specific passcode:
PYTHONPATH=src python3 -m fuel_optimizer.web_build --passcode my-new-pass
```

Run it whenever the source pricing changes — e.g., on the next weekly
Pilot drop. Commit the resulting `data.enc.json` and `cities.csv`.

## How the routing works

1. **Geocode** origin + destination locally from `cities.csv` (plus a
   small hand-coded table covering Brampton / Mississauga / Toronto,
   since the CSV is US-only).
2. **OSRM** call: `GET /route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson&steps=true`
   → returns the full polyline and turn-by-turn step list. Uses the
   project's public demo server — no API key.
3. **Match stations** to the polyline: for each Pilot site, find the
   nearest polyline vertex (haversine) and its cumulative distance from
   origin. Sites within 20 mi of any vertex are "on route" with that
   cumulative distance as the mile marker.
4. **Optimize** with the greedy gas-station algorithm — same code path
   as the CLI tool, ported to JS in `app.js`.
5. **Render** the route line in cyan, all on-route stations as colored
   circles (green = cheap → red = expensive), optimal stops as larger
   white-outlined circles. Sidebar shows total cost, savings vs.
   average-priced fill baseline, stop list, and the OSRM step list
   formatted into English.

## Operational notes

- **OSRM public demo** is rate-limited and not officially supported for
  production. For real volume, swap `OSRM_BASE` in `app.js` for a paid
  routing service (Mapbox, OpenRouteService) or a self-hosted OSRM.
- **Detour radius** is hard-coded at 20 mi (line in `app.js`:
  `findStationsAlongRoute(route, STATIONS, 20)`). Bump it up for routes
  in sparser Pilot regions.
- **Truck defaults**: 200 gal × 6.5 mpg = 1300 mi range, 20 gal
  reserve at destination. All overridable in the UI.
- **Mobile**: layout collapses below 900 px (map on top, sidebar
  beneath).
