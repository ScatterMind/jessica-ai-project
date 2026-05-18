"""Load Pilot Flying J site/price data from the corpus XLS."""
from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import xlrd


@dataclass(frozen=True)
class PilotSite:
    site_code: str
    city: str
    state: str
    your_price: float
    retail_price: float
    rack_city: str
    rack_state: str


@contextmanager
def _silence_fd1():
    """xlrd writes its sector-size warning straight to fd 1, bypassing
    sys.stdout — so contextlib.redirect_stdout won't catch it. Redirect
    the file descriptor itself."""
    saved = os.dup(1)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)
    try:
        yield
    finally:
        os.dup2(saved, 1)
        os.close(saved)
        os.close(devnull)


def load_pilot_sites(xls_path: Path) -> list[PilotSite]:
    with _silence_fd1():
        book = xlrd.open_workbook(str(xls_path))
    sheet = book.sheet_by_index(0)
    sites: list[PilotSite] = []
    for r in range(6, sheet.nrows):
        code = sheet.cell_value(r, 0)
        if not code:
            continue
        sites.append(
            PilotSite(
                site_code=str(code).split(".")[0],
                city=str(sheet.cell_value(r, 1)).strip(),
                state=str(sheet.cell_value(r, 2)).strip(),
                your_price=float(sheet.cell_value(r, 19)),
                retail_price=float(sheet.cell_value(r, 17)),
                rack_city=str(sheet.cell_value(r, 5)).strip(),
                rack_state=str(sheet.cell_value(r, 6)).strip(),
            )
        )
    return sites
