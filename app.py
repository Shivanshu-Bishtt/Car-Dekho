"""app.py — Streamlit frontend for Car Match."""

import streamlit as st
import pandas as pd
from database import get_all_cars
from score import score_cars

st.set_page_config(page_title="Car Match", layout="centered")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _goto(step):
    st.session_state.step = step
    st.rerun()

def _price_label(price):
    lakhs = price / 100_000
    return f"Rs. {lakhs:.1f}L" if lakhs < 100 else f"Rs. {lakhs/100:.2f}Cr"

def _mileage_label(car):
    return "Electric" if car["fuel_type"] == "EV" else f"{car['mileage_kmpl']} kmpl"

def _stars(n, total=5):
    return "★" * n + "☆" * (total - n)

# ---------------------------------------------------------------------------
# Bootstrap session state
# ---------------------------------------------------------------------------

if "step" not in st.session_state:
    st.session_state.step = "welcome"

step = st.session_state.step

# ---------------------------------------------------------------------------
# Welcome
# ---------------------------------------------------------------------------

if step == "welcome":
    st.title("Car Match")
    st.subheader("From confused to a confident shortlist — in five questions.")
    st.write(
        "Tell us how you plan to use the car and what matters most to you. "
        "We’ll score every car in the database against your answers and "
        "surface your best matches."
    )
    st.write("")
    if st.button("Start", type="primary", use_container_width=True):
        _goto("q1")

# ---------------------------------------------------------------------------
# Q1 — Budget
# ---------------------------------------------------------------------------

elif step == "q1":
    st.caption("Question 1 of 5")
    st.progress(0.2)
    st.header("What is your maximum budget?")
    st.write("We’ll only show cars that fit within this number.")

    default = st.session_state.get("budget_max", 1_500_000)
    budget = st.slider(
        "Budget",
        min_value=300_000,
        max_value=6_000_000,
        value=default,
        step=100_000,
        label_visibility="collapsed",
    )
    st.metric("Selected budget", _price_label(budget))

    if st.button("Next", type="primary"):
        st.session_state.budget_max = budget
        _goto("q2")

# ---------------------------------------------------------------------------
# Q2 — Primary use
# ---------------------------------------------------------------------------

elif step == "q2":
    st.caption("Question 2 of 5")
    st.progress(0.4)
    st.header("How will you mainly use the car?")

    use_options = ["city", "highway", "family", "mixed"]
    use_labels = {
        "city":    "City — short trips, heavy traffic, tight parking",
        "highway": "Highway — long drives and open roads",
        "family":  "Family — school runs, weekend trips, lots of passengers",
        "mixed":   "Mixed — a bit of everything",
    }
    default_idx = use_options.index(st.session_state.get("primary_use", "mixed"))
    chosen_use = st.radio(
        "Primary use",
        options=use_options,
        index=default_idx,
        format_func=lambda x: use_labels[x],
        label_visibility="collapsed",
    )

    if st.button("Next", type="primary"):
        st.session_state.primary_use = chosen_use
        _goto("q3")

# ---------------------------------------------------------------------------
# Q3 — Seats needed
# ---------------------------------------------------------------------------

elif step == "q3":
    st.caption("Question 3 of 5")
    st.progress(0.6)
    st.header("How many seats do you need at minimum?")
    st.write("Cars with fewer seats than this will be filtered out.")

    seat_options = [2, 4, 5, 6, 7]
    default_seats = st.session_state.get("seats_needed", 5)
    chosen_seats = st.selectbox(
        "Minimum seats",
        options=seat_options,
        index=seat_options.index(default_seats),
        label_visibility="collapsed",
    )

    if st.button("Next", type="primary"):
        st.session_state.seats_needed = chosen_seats
        _goto("q4")

# ---------------------------------------------------------------------------
# Q4 — Fuel preference
# ---------------------------------------------------------------------------

elif step == "q4":
    st.caption("Question 4 of 5")
    st.progress(0.8)
    st.header("Do you have a fuel-type preference?")

    fuel_options = ["No preference", "Petrol", "Diesel", "EV", "Hybrid"]
    default_fuel_idx = fuel_options.index(
        st.session_state.get("fuel_preference", "No preference")
    )
    chosen_fuel = st.radio(
        "Fuel preference",
        options=fuel_options,
        index=default_fuel_idx,
        label_visibility="collapsed",
    )

    if st.button("Next", type="primary"):
        st.session_state.fuel_preference = chosen_fuel
        _goto("q5")

# ---------------------------------------------------------------------------
# Q5 — Top priority
# ---------------------------------------------------------------------------

elif step == "q5":
    st.caption("Question 5 of 5")
    st.progress(1.0)
    st.header("What matters most to you?")
    st.write("This carries the most weight in the final score.")

    priority_options = ["safety", "mileage", "space", "value"]
    priority_labels = {
        "safety":  "Safety — highest crash-test ratings first",
        "mileage": "Mileage — lowest running cost per kilometre",
        "space":   "Space — most room for passengers and luggage",
        "value":   "Value — best quality for the money",
    }
    default_priority_idx = priority_options.index(
        st.session_state.get("priority", "safety")
    )
    chosen_priority = st.radio(
        "Priority",
        options=priority_options,
        index=default_priority_idx,
        format_func=lambda x: priority_labels[x],
        label_visibility="collapsed",
    )

    if st.button("Find my matches", type="primary", use_container_width=True):
        st.session_state.priority = chosen_priority
        _goto("results")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

elif step == "results":
    prefs = {
        "budget_max":      st.session_state.get("budget_max",      1_500_000),
        "primary_use":     st.session_state.get("primary_use",     "mixed"),
        "seats_needed":    st.session_state.get("seats_needed",    5),
        "fuel_preference": st.session_state.get("fuel_preference", "No preference"),
        "priority":        st.session_state.get("priority",        "safety"),
    }

    results = score_cars(get_all_cars(), prefs)

    st.title("Your Top Matches")

    # One-line summary of active filters
    st.caption(
        f"Budget: {_price_label(prefs['budget_max'])}"
        f"  |  Use: {prefs['primary_use'].title()}"
        f"  |  Seats: {prefs['seats_needed']}+"
        f"  |  Fuel: {prefs['fuel_preference']}"
        f"  |  Priority: {prefs['priority'].title()}"
    )
    st.write("")

    if not results:
        st.warning(
            "No cars matched your filters. "
            "Try raising your budget or reducing the minimum number of seats."
        )
    else:
        # ── Car cards ──────────────────────────────────────────────────────
        for car in results:
            with st.container(border=True):
                # Heading row: name left, score right
                col_name, col_score = st.columns([3, 1])
                with col_name:
                    st.subheader(f"{car['make']} {car['model']}")
                    st.caption(car["variant"])
                with col_score:
                    st.metric("Match score", f"{car['score']} / 100")

                st.write(f"**Price: {_price_label(car['price'])}**")

                # Key specs across five equal columns
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Fuel",    car["fuel_type"])
                c2.metric("Seats",   car["seats"])
                c3.metric("Body",    car["body_type"])
                c4.metric("Mileage", _mileage_label(car))
                c5.metric("Safety",  _stars(car["safety_rating"]))

                # Reason sentence
                st.info(car["reason"])

        # ── Comparison table ───────────────────────────────────────────────
        st.write("")
        st.subheader("Side-by-side comparison")

        comparison_df = pd.DataFrame([
            {
                "Car":         f"{r['make']} {r['model']}",
                "Variant":     r["variant"],
                "Price (L)":   round(r["price"] / 100_000, 1),
                "Fuel":        r["fuel_type"],
                "Seats":       r["seats"],
                "Body":        r["body_type"],
                "Mileage":     r["mileage_kmpl"] if r["fuel_type"] != "EV" else "EV",
                "Safety":      _stars(r["safety_rating"]),
                "Score":       r["score"],
            }
            for r in results
        ])
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # ── Start over ─────────────────────────────────────────────────────────
    st.write("")
    if st.button("Start over", use_container_width=True):
        for key in ["step", "budget_max", "primary_use", "seats_needed",
                    "fuel_preference", "priority"]:
            st.session_state.pop(key, None)
        st.rerun()
