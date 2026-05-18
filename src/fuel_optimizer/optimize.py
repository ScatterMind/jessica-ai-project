"""
Gas-station problem: optimal refueling under continuous fueling.

Given a route of length D and stations at positions s_i with prices p_i,
the greedy "look-ahead" strategy is provably optimal (Khuller, Malekian
& Mestre, 2007):

  At each station i:
    - If a cheaper station exists within tank range, buy just enough
      fuel to reach it.
    - Otherwise, fill the tank (or buy only enough to reach the
      destination, whichever is less).

This module assumes continuous fueling (any gallon amount), no detour
cost (stations are exactly on-route), and constant mpg.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Station:
    name: str
    miles: float
    price: float  # $/gal


@dataclass
class FuelStop:
    station: Station
    gallons: float
    cost: float


@dataclass
class Plan:
    stops: list[FuelStop] = field(default_factory=list)
    total_cost: float = 0.0
    total_gallons: float = 0.0
    arrival_fuel_gallons: float = 0.0
    feasible: bool = True
    error: Optional[str] = None


def optimize(
    total_miles: float,
    stations: list[Station],
    tank_gallons: float = 200.0,
    mpg: float = 6.5,
    start_gallons: Optional[float] = None,
    reserve_gallons: float = 20.0,
) -> Plan:
    """Run the greedy gas-station optimizer.

    Parameters
    ----------
    total_miles      : route length, miles.
    stations         : on-route stations, in any order. Each has a mile
                       marker (0 = start, total_miles = destination) and
                       a price in $/gal.
    tank_gallons     : tank capacity in gallons.
    mpg              : fuel economy.
    start_gallons    : fuel on departure. Defaults to a full tank.
    reserve_gallons  : minimum fuel to arrive with.
    """
    if start_gallons is None:
        start_gallons = tank_gallons
    tank_miles = tank_gallons * mpg
    reserve_miles = reserve_gallons * mpg

    on_route = sorted(
        [s for s in stations if 0 <= s.miles <= total_miles],
        key=lambda s: s.miles,
    )

    fuel_miles = start_gallons * mpg
    pos = 0.0
    plan = Plan()

    for i, st in enumerate(on_route):
        leg = st.miles - pos
        if leg > fuel_miles + 1e-6:
            plan.feasible = False
            plan.error = (
                f"Out of fuel between mile {pos:.0f} and {st.name} at mile "
                f"{st.miles:.0f}: need {leg:.0f} mi, have "
                f"{fuel_miles:.0f}."
            )
            return plan
        fuel_miles -= leg
        pos = st.miles

        # Look ahead for the first cheaper station within tank reach.
        cheaper_at: Optional[float] = None
        max_reach = pos + tank_miles
        for nxt in on_route[i + 1 :]:
            if nxt.miles > max_reach:
                break
            if nxt.price < st.price:
                cheaper_at = nxt.miles
                break

        miles_to_dest = total_miles - pos

        if cheaper_at is not None:
            # Buy just enough to reach the cheaper station.
            target_after = cheaper_at - pos
        elif miles_to_dest + reserve_miles <= tank_miles:
            # Destination reachable with reserve — fill exactly for that.
            target_after = miles_to_dest + reserve_miles
        else:
            # No cheaper option, can't reach destination — fill the tank.
            target_after = tank_miles

        to_buy_miles = max(0.0, target_after - fuel_miles)
        gallons = to_buy_miles / mpg
        if gallons > 0.01:
            cost = gallons * st.price
            plan.stops.append(FuelStop(station=st, gallons=gallons, cost=cost))
            plan.total_cost += cost
            plan.total_gallons += gallons
            fuel_miles += to_buy_miles

    # Final leg to destination.
    leg = total_miles - pos
    if leg > fuel_miles + 1e-6:
        plan.feasible = False
        plan.error = (
            f"Out of fuel between mile {pos:.0f} and destination at mile "
            f"{total_miles:.0f}: need {leg:.0f} mi, have {fuel_miles:.0f}."
        )
        return plan
    plan.arrival_fuel_gallons = (fuel_miles - leg) / mpg
    return plan
