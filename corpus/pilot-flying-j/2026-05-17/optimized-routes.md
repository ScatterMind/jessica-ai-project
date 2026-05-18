# Optimized fueling — 2026-05-17 Pilot Flying J prices

Source data: `cp149834.xls` (account 149834 — KJS Transport Inc., effective 2026-05-17 → 2026-05-18). **Confidential** — vendor pricing is under the proposal-letter confidentiality clause; do not republish.

Tool: `src/fuel_optimizer/`. Algorithm: greedy look-ahead (Khuller, Malekian & Mestre 2007), provably optimal under continuous fueling, on-route stations only, constant mpg.

Assumptions: 200 gal tank · 6.5 mpg · 1300 mi range · 20 gal reserve at destination · ≤50 mi detour to qualify as on-route · great-circle distance as mile-marker proxy.

Re-run: `PYTHONPATH=src python3 -m fuel_optimizer --markdown` (add `--start-gallons N` to vary).

---

## Scenario A — Starting with a full tank (200 gal)

Short routes (under ~1100 mi) don't need any fueling; longer hauls show where the optimizer earns its keep.

### Brampton → Detroit

- **Origin → Destination:** Brampton, ON → Detroit, MI
- **Great-circle distance:** 192 mi
- **Pilot sites on route:** 2 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Short cross-border haul out of home terminal.

_No fuel stops needed — destination within starting-tank range._

_Arrival fuel: ~170 gal._

### Brampton → Atlanta

- **Origin → Destination:** Brampton, ON → Atlanta, GA
- **Great-circle distance:** 733 mi
- **Pilot sites on route:** 78 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Southeast long-haul out of home terminal.

_No fuel stops needed — destination within starting-tank range._

_Arrival fuel: ~87 gal._

### Atlanta → Brampton

- **Origin → Destination:** Atlanta, GA → Brampton, ON
- **Great-circle distance:** 733 mi
- **Pilot sites on route:** 78 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Northbound return to home terminal.

_No fuel stops needed — destination within starting-tank range._

_Arrival fuel: ~87 gal._

### Chicago → Dallas

- **Origin → Destination:** Chicago, IL → Dallas, TX
- **Great-circle distance:** 805 mi
- **Pilot sites on route:** 81 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Midwest → south-central intercity haul.

_No fuel stops needed — destination within starting-tank range._

_Arrival fuel: ~76 gal._

### Los Angeles → Atlanta

- **Origin → Destination:** Los Angeles, CA → Atlanta, GA
- **Great-circle distance:** 1933 mi
- **Pilot sites on route:** 168 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Transcontinental west-to-southeast.

| Mile | Stop | Gal | $/gal | Cost |
|-----:|:-----|----:|------:|-----:|
| 1238 | #433 Dallas, TX | 0.5 | $4.602 | $2.25 |
| 1303 | #157 Sulphur Springs, TX | 12.8 | $4.596 | $58.72 |
| 1386 | #1470 Carthage, TX | 73.0 | $4.541 | $331.64 |
| 1861 | #415 Rising Fawn, GA | 4.5 | $4.480 | $19.94 |
| 1890 | #421 Dalton, GA | 26.7 | $4.475 | $119.51 |
| | **Total** | **117.5** | | **$532.07** |

_Arrival fuel: ~20 gal._

### Seattle → Phoenix

- **Origin → Destination:** Seattle, WA → Phoenix, AZ
- **Great-circle distance:** 1115 mi
- **Pilot sites on route:** 40 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Pacific-NW → southwest.

_No fuel stops needed — destination within starting-tank range._

_Arrival fuel: ~29 gal._

### Miami → New York

- **Origin → Destination:** Miami, FL → New York, NY
- **Great-circle distance:** 1094 mi
- **Pilot sites on route:** 36 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* East-coast northbound.

_No fuel stops needed — destination within starting-tank range._

_Arrival fuel: ~32 gal._

---

## Scenario B — Starting with 50 gal (forces refueling on every route)

Realistic if a leg started elsewhere and the truck enters this route near-empty. The greedy 'buy just enough to reach the next cheaper station' rule is visible as a descending-price chain on the long hauls.

### Brampton → Detroit

- **Origin → Destination:** Brampton, ON → Detroit, MI
- **Great-circle distance:** 192 mi
- **Pilot sites on route:** 2 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Short cross-border haul out of home terminal.

_No fuel stops needed — destination within starting-tank range._

_Arrival fuel: ~20 gal._

### Brampton → Atlanta

- **Origin → Destination:** Brampton, ON → Atlanta, GA
- **Great-circle distance:** 733 mi
- **Pilot sites on route:** 78 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Southeast long-haul out of home terminal.

| Mile | Stop | Gal | $/gal | Cost |
|-----:|:-----|----:|------:|-----:|
| 283 | #503 Morgantown, WV | 11.4 | $5.174 | $58.72 |
| 399 | #660 Catlettsburg, KY | 7.7 | $5.011 | $38.45 |
| 449 | #041 Mt Sterling, KY | 1.1 | $4.959 | $5.51 |
| 456 | #047 Georgetown, KY | 2.8 | $4.954 | $13.87 |
| 474 | #750 Fort Chiswell, VA | 11.3 | $4.901 | $55.50 |
| 548 | #051 Greeneville, TN | 1.2 | $4.698 | $5.79 |
| 556 | #1577 Pioneer, TN | 3.8 | $4.663 | $17.59 |
| 580 | #219 Knoxville, TN | 14.1 | $4.661 | $65.79 |
| 672 | #628 Carnesville, GA | 1.0 | $4.583 | $4.72 |
| 679 | #421 Dalton, GA | 28.3 | $4.475 | $126.69 |
| | **Total** | **82.7** | | **$392.62** |

_Arrival fuel: ~20 gal._

### Atlanta → Brampton

- **Origin → Destination:** Atlanta, GA → Brampton, ON
- **Great-circle distance:** 733 mi
- **Pilot sites on route:** 78 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Northbound return to home terminal.

| Mile | Stop | Gal | $/gal | Cost |
|-----:|:-----|----:|------:|-----:|
| 77 | #421 Dalton, GA | 82.7 | $4.475 | $370.17 |
| | **Total** | **82.7** | | **$370.17** |

_Arrival fuel: ~20 gal._

### Chicago → Dallas

- **Origin → Destination:** Chicago, IL → Dallas, TX
- **Great-circle distance:** 805 mi
- **Pilot sites on route:** 81 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Midwest → south-central intercity haul.

| Mile | Stop | Gal | $/gal | Cost |
|-----:|:-----|----:|------:|-----:|
| 230 | #675 Wayland, MO | 1.9 | $4.859 | $9.12 |
| 337 | #044 Boonville, MO | 5.8 | $4.830 | $27.82 |
| 375 | #443 Higginsville, MO | 19.5 | $4.781 | $93.15 |
| 501 | #1440 Bald Knob, AR | 7.9 | $4.730 | $37.20 |
| 552 | #332 North Little Rock, AR | 3.1 | $4.725 | $14.43 |
| 572 | #118 Benton, AR | 1.1 | $4.720 | $5.38 |
| 580 | #196 Roland, OK | 2.4 | $4.715 | $11.55 |
| 596 | #259 Muskogee, OK | 2.7 | $4.633 | $12.51 |
| 613 | #492 Arkadelphia, AR | 20.1 | $4.631 | $92.87 |
| 743 | #1289 Denison, TX | 0.3 | $4.627 | $1.31 |
| 745 | #157 Sulphur Springs, TX | 29.2 | $4.596 | $134.10 |
| | **Total** | **93.8** | | **$439.43** |

_Arrival fuel: ~20 gal._

### Los Angeles → Atlanta

- **Origin → Destination:** Los Angeles, CA → Atlanta, GA
- **Great-circle distance:** 1933 mi
- **Pilot sites on route:** 168 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Transcontinental west-to-southeast.

| Mile | Stop | Gal | $/gal | Cost |
|-----:|:-----|----:|------:|-----:|
| 226 | #1208 Yuma, AZ | 36.3 | $5.128 | $186.06 |
| 561 | #163 Lordsburg, NM | 17.5 | $5.077 | $88.97 |
| 675 | #266 Las Cruces, NM | 2.1 | $5.012 | $10.69 |
| 689 | #435 Anthony, TX | 21.8 | $4.972 | $108.20 |
| 830 | #691 Tucumcari, NM | 9.3 | $4.851 | $45.04 |
| 890 | #1147 Kermit, TX | 3.8 | $4.720 | $17.80 |
| 915 | #1211 Andrews, TX | 2.6 | $4.700 | $12.30 |
| 932 | #580 Odessa, TX | 38.0 | $4.692 | $178.23 |
| 1179 | #704 Edmond, OK | 1.0 | $4.659 | $4.79 |
| 1185 | #206 Weatherford, TX | 8.0 | $4.615 | $37.03 |
| 1238 | #433 Dallas, TX | 10.1 | $4.602 | $46.41 |
| 1303 | #157 Sulphur Springs, TX | 12.8 | $4.596 | $58.72 |
| 1386 | #1470 Carthage, TX | 73.0 | $4.541 | $331.64 |
| 1861 | #415 Rising Fawn, GA | 4.5 | $4.480 | $19.94 |
| 1890 | #421 Dalton, GA | 26.7 | $4.475 | $119.51 |
| | **Total** | **267.5** | | **$1265.33** |

_Arrival fuel: ~20 gal._

### Seattle → Phoenix

- **Origin → Destination:** Seattle, WA → Phoenix, AZ
- **Great-circle distance:** 1115 mi
- **Pilot sites on route:** 40 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* Pacific-NW → southwest.

| Mile | Stop | Gal | $/gal | Cost |
|-----:|:-----|----:|------:|-----:|
| 166 | #584 Aurora, OR | 141.5 | $4.922 | $696.46 |
| | **Total** | **141.5** | | **$696.46** |

_Arrival fuel: ~20 gal._

### Miami → New York

- **Origin → Destination:** Miami, FL → New York, NY
- **Great-circle distance:** 1094 mi
- **Pilot sites on route:** 36 (≤50 mi detour; 0 ungeocoded globally)
- **Truck:** tank 200 gal × 6.5 mpg = 1300 mi range
- *Note:* East-coast northbound.

| Mile | Stop | Gal | $/gal | Cost |
|-----:|:-----|----:|------:|-----:|
| 10 | #897 Opa Locka, FL | 24.5 | $4.932 | $120.61 |
| 484 | #1082 Charleston, SC | 15.0 | $4.924 | $73.73 |
| 581 | #062 Florence, SC | 98.9 | $4.761 | $470.58 |
| | **Total** | **138.3** | | **$664.92** |

_Arrival fuel: ~20 gal._

