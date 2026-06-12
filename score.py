"""
score.py — pure recommendation engine for the CarDekho advisor.
No database access; operates on plain list-of-dicts from get_all_cars().
"""

# ---------------------------------------------------------------------------
# Weight constants — must sum to 100
# ---------------------------------------------------------------------------
W_BUDGET   = 25   # headroom under the stated budget
W_FUEL     = 15   # fuel-type match
W_USE      = 20   # how well the car suits the stated primary use
W_PRIORITY = 40   # user's chosen priority (deliberately the heaviest)

# ---------------------------------------------------------------------------
# Body-type suitability per primary_use  (0.0 – 1.0)
# ---------------------------------------------------------------------------
BODY_FIT = {
    "city":    {"Hatchback": 1.0, "Sedan": 0.7, "SUV": 0.4, "MPV": 0.3},
    "highway": {"Sedan": 1.0,     "SUV": 0.8,   "MPV": 0.7, "Hatchback": 0.5},
    "family":  {"MPV": 1.0,       "SUV": 0.9,   "Sedan": 0.4, "Hatchback": 0.2},
    "mixed":   {"SUV": 0.9,       "MPV": 0.8,   "Sedan": 0.7, "Hatchback": 0.6},
}

# Sub-component mix for the use-fit score (values must sum to 1.0 per use)
USE_WEIGHTS = {
    "city":    {"mileage": 0.50, "body": 0.30, "safety": 0.20},
    "highway": {"mileage": 0.40, "safety": 0.40, "body": 0.20},
    "family":  {"seats": 0.40,  "safety": 0.40, "body": 0.20},
    "mixed":   {"mileage": 0.25, "safety": 0.30, "seats": 0.20, "body": 0.25},
}


def score_cars(cars, prefs):
    """
    Filter and score a list of car dicts against user preferences.

    Parameters
    ----------
    cars  : list[dict]  — raw records from get_all_cars()
    prefs : dict with keys:
        budget_max       (int)  — maximum price in INR
        primary_use      (str)  — 'city' | 'highway' | 'family' | 'mixed'
        seats_needed     (int)  — minimum seat count required
        fuel_preference  (str)  — fuel type string or 'No preference'
        priority         (str)  — 'safety' | 'mileage' | 'space' | 'value'

    Returns
    -------
    list[dict]  — up to 5 cars sorted by score desc; each dict has the
                  original car fields plus 'score' (int 0-100) and
                  'reason' (one plain-English sentence).
    """
    budget_max  = prefs["budget_max"]
    primary_use = prefs["primary_use"]
    seats_needed = prefs["seats_needed"]
    fuel_pref   = prefs["fuel_preference"]
    priority    = prefs["priority"]

    # ------------------------------------------------------------------
    # 1. Hard filter
    # ------------------------------------------------------------------
    filtered = [
        c for c in cars
        if c["price"] <= budget_max and c["seats"] >= seats_needed
    ]
    if not filtered:
        return []

    # ------------------------------------------------------------------
    # Normalisation helpers — computed against the filtered set so that
    # scores are relative to what the user can actually afford/access.
    # ------------------------------------------------------------------
    non_ev_mileages = [c["mileage_kmpl"] for c in filtered if c["fuel_type"] != "EV"]
    max_mileage = max(non_ev_mileages) if non_ev_mileages else 1.0
    max_seats   = max(c["seats"] for c in filtered)

    def _mileage_norm(car):
        # EVs are treated as the most efficient option (full score).
        if car["fuel_type"] == "EV":
            return 1.0
        return car["mileage_kmpl"] / max_mileage if max_mileage else 0.0

    def _safety_norm(car):
        # Maps safety_rating 1-5 → 0.0-1.0
        return (car["safety_rating"] - 1) / 4.0

    def _seats_norm(car):
        return car["seats"] / max_seats if max_seats else 0.0

    def _budget_norm(car):
        # Square-root curve: a car well under budget rewards more than a
        # linear scale, reflecting real "comfort" vs "right at the edge".
        return (1.0 - car["price"] / budget_max) ** 0.5

    def _fuel_norm(car):
        if fuel_pref == "No preference" or car["fuel_type"] == fuel_pref:
            return 1.0
        return 0.0

    def _body_fit(car):
        return BODY_FIT.get(primary_use, {}).get(car["body_type"], 0.5)

    def _use_score(car):
        sub = {
            "mileage": _mileage_norm(car),
            "safety":  _safety_norm(car),
            "seats":   _seats_norm(car),
            "body":    _body_fit(car),
        }
        w = USE_WEIGHTS[primary_use]
        return sum(w.get(k, 0.0) * v for k, v in sub.items())

    def _priority_score(car):
        if priority == "safety":
            return _safety_norm(car)
        if priority == "mileage":
            return _mileage_norm(car)
        if priority == "space":
            return _seats_norm(car)
        if priority == "value":
            # Value = quality relative to price paid.
            return _safety_norm(car) * 0.4 + _budget_norm(car) * 0.6
        return 0.0

    def _total(car):
        return (
            W_BUDGET   * _budget_norm(car)
            + W_FUEL   * _fuel_norm(car)
            + W_USE    * _use_score(car)
            + W_PRIORITY * _priority_score(car)
        )

    # ------------------------------------------------------------------
    # 2. Score every car and pick the top 5
    # ------------------------------------------------------------------
    scored = sorted(
        [{**car, "_raw": _total(car)} for car in filtered],
        key=lambda c: c["_raw"],
        reverse=True,
    )[:5]

    # ------------------------------------------------------------------
    # 3. Attach human-readable reason and clean up scratch field
    # ------------------------------------------------------------------
    for car in scored:
        car["score"] = round(car["_raw"])
        car["reason"] = _build_reason(car, prefs, budget_max)
        del car["_raw"]

    return scored


# ---------------------------------------------------------------------------
# Reason builder — kept separate so it can be tested independently
# ---------------------------------------------------------------------------

def _build_reason(car, prefs, budget_max):
    """Return a one-sentence explanation for why this car was recommended."""
    priority  = prefs["priority"]
    use       = prefs["primary_use"]
    headroom  = round((1 - car["price"] / budget_max) * 100)
    price_L   = car["price"] / 100_000  # convert to lakhs

    if priority == "safety":
        if car["safety_rating"] == 5:
            return (
                f"Top safety pick with a perfect 5/5 NCAP rating, "
                f"₹{price_L:.1f}L — {headroom}% under your budget."
            )
        return (
            f"Strong {car['safety_rating']}/5 safety score, "
            f"₹{price_L:.1f}L with {headroom}% budget headroom."
        )

    if priority == "mileage":
        if car["fuel_type"] == "EV":
            return (
                f"Zero fuel cost EV — lowest running expense in the list, "
                f"comfortably at ₹{price_L:.1f}L ({headroom}% under budget)."
            )
        return (
            f"Best efficiency pick at {car['mileage_kmpl']} kmpl — "
            f"₹{price_L:.1f}L with {headroom}% budget headroom."
        )

    if priority == "space":
        return (
            f"Spacious {car['seats']}-seat {car['body_type'].lower()} "
            f"at ₹{price_L:.1f}L, {headroom}% under your budget."
        )

    if priority == "value":
        return (
            f"Best value option — {car['safety_rating']}/5 safety at just "
            f"₹{price_L:.1f}L, {headroom}% under budget."
        )

    # Fallback: use-case driven
    if use == "city":
        return (
            f"City-friendly {car['body_type'].lower()} at ₹{price_L:.1f}L "
            f"with {car['mileage_kmpl']} kmpl running cost."
        )
    if use == "highway":
        return (
            f"Highway-capable {car['body_type'].lower()} with "
            f"{car['mileage_kmpl']} kmpl and {car['safety_rating']}/5 safety."
        )
    if use == "family":
        return (
            f"Family-ready {car['seats']}-seat {car['body_type'].lower()} "
            f"with {car['safety_rating']}/5 safety at ₹{price_L:.1f}L."
        )
    return (
        f"Balanced all-rounder — {car['body_type']} at ₹{price_L:.1f}L "
        f"suiting your {use} driving needs."
    )


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    from database import get_all_cars

    prefs = {
        "budget_max": 2_000_000,
        "primary_use": "family",
        "seats_needed": 6,
        "fuel_preference": "No preference",
        "priority": "safety",
    }
    results = score_cars(get_all_cars(), prefs)
    print(f"Top {len(results)} recommendations:\n")
    for i, car in enumerate(results, 1):
        print(
            f"{i}. {car['make']} {car['model']} {car['variant']}"
            f"  |  score={car['score']}  |  ₹{car['price']//100000}L"
        )
        print(f"   {car['reason']}\n")
