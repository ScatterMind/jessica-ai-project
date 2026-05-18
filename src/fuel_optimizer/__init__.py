"""Gas-price-optimal refueling planner.

Built for KJS Transport (home terminal: Brampton, ON) but the optimizer
itself is route-agnostic — it works on any A → B haul. The built-in
sample set in routes.py mixes Brampton-involving legs (out of and back
to the home terminal) with pure US-US intercity runs.
"""
