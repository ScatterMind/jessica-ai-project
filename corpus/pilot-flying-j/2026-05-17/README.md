# Pilot Flying J price report — week of 2026-05-17

**Confidential.** Vendor cover note references "all terms and conditions
of your proposal letter, including definitions and confidentiality."
Treat this whole folder as proprietary KJS Transport / Pilot Flying J
material — never copy any of it into `site/`.

## Source
- File: `cp149834.xls` (Excel 97–2003 BIFF, 286 KB)
- Account: **149834 — KJS Transport Inc.**
- Effective: **2026-05-17 → 2026-05-18** (~24-hour quote window)
- Retail snapshot taken: 2026-05-16 19:21
- Price source: **OPIS Contract Avg.**
- Report type: "Better Of Pricing Report"

## Vendor cover note (verbatim)
> PILOT US PRICING: Please find attached your Pilot Flying J price
> report. \*\*\*\*All diesel prices quoted are for Ultra Low Sulphur
> Diesel No. 2 with biodiesel, as blended by each State or Province. If
> you purchase Diesel No. 1, you will be charged a different price. All
> terms and conditions of your proposal letter, including definitions
> and confidentiality, shall apply to this price quote. Please contact
> your Pilot Flying J sales representative if you have any questions or
> comments.

## What's in the workbook
Single sheet (`Daily Price Quote - Better Of -`), 691 rows × 21 cols.
- Rows 0–4: title/metadata banner (account, effective dates, snapshot timestamp).
- Row 5: column header.
- Rows 6–689: **684 site rows**, one per Pilot truck-stop offering DSL.
- Row 690: blank tail.

### Columns
| # | Field | Notes |
|---|-------|-------|
| 1  | Site                          | 3–4 digit Pilot site code |
| 2  | City                          | |
| 3  | ST                            | State / province |
| 4  | Prod                          | `DSL` everywhere in this report |
| 5  | Rack ID                       | Source rack identifier |
| 6  | Rack City                     | |
| 7  | Rack ST                       | |
| 8  | Cost                          | Wholesale per gal before tax/fees |
| 9  | Federal Tax/Fees              | $0.244 everywhere (federal diesel tax) |
| 10 | State Tax/Fees                | |
| 11 | Sales Tax/Fees                | Mostly $0 |
| 12 | Lust/Insp Super Fund/Fees     | |
| 13 | Freight                       | |
| 14 | Pump Fee                      | Consistently **−$0.05** (flat per-gal credit) |
| 15 | *(blank column)*              | |
| 16 | Other                         | |
| 17 | Total Cost                    | Sum of cost + taxes + fees |
| 18 | Retail Price                  | Posted pump price |
| 19 | Disc Retail                   | = Retail in this report (no separate discount applied) |
| 20 | **Your Price**                | What KJS pays per gal |
| 21 | **Savings Total**             | Retail − Your Price |

## Quick stats (684 sites)
| Metric              | min     | max     | mean    | median  |
|---------------------|---------|---------|---------|---------|
| Retail $/gal        | 5.099   | 7.659   | 5.805   | 5.659   |
| Your Price $/gal    | 4.475   | 6.939   | 5.144   | 4.971   |
| Savings $/gal       | 0.000   | 1.305   | ~0.66   | 0.699   |

- **9 sites quote zero savings** (Pilot retail = Your Price): all in MT
  (Milltown, Superior, Missoula, Lolo, Sidney), plus Post Falls ID,
  Newark NJ, Tacoma WA, Tucson AZ. Likely low-volume / no-rack-discount
  markets.
- **Top savings (~$1.30/gal)**: site 784 North East MD, site 1194
  Phoenix AZ — these are the standout fill-up locations on this report.
- Pump Fee `−$0.05` everywhere reads as a flat per-gal rebate already
  baked into Your Price.

## Coverage (43 states)
TX 92 · IL 38 · OH 37 · CA 34 · GA 31 · AZ 30 · IN 27 · FL 27 · KY 25
· SC 22 · TN 21 · MO 19 · VA 19 · NC 17 · MT 17 · PA 16 · IA 16 ·
remainder ≤13 each.

Sparse / absent: WV (3), CT (1), MA (2); no AK, HI, ME, NH, RI, VT, DE
— gaps in Pilot's network, not the report.

## Reproducing the read
```python
import xlrd
b = xlrd.open_workbook("cp149834.xls")
s = b.sheet_by_index(0)
header = [s.cell_value(5, c) for c in range(s.ncols)]
rows = [[s.cell_value(r, c) for c in range(s.ncols)]
        for r in range(6, s.nrows) if s.cell_value(r, 0)]
```
(Generates 684 data rows. xlrd ≥2.0 supports .xls; .xlsx is unsupported there.)
