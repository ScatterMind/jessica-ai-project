# US cities reference data

`us_cities.csv` — 29,880 US cities with state, county, lat/lon. Used
by `src/fuel_optimizer/` to geocode Pilot Flying J site cities.

- Source: <https://github.com/kelvins/US-Cities-Database> (commit on
  the `main` branch as of 2026-05-18).
- License: MIT (per the upstream repo).
- Columns: `ID, STATE_CODE, STATE_NAME, CITY, COUNTY, LATITUDE, LONGITUDE`.

Coverage of Pilot's site cities is ~96% direct, ~98% with simple
`St`/`Saint` and `Mt`/`Mount` normalization. The remaining ~2% are
small truck-stop hamlets the optimizer simply excludes (they don't
participate as fuel-stop candidates).

Refresh: `curl -sS https://raw.githubusercontent.com/kelvins/US-Cities-Database/main/csv/us_cities.csv -o corpus/geo/us_cities.csv`
