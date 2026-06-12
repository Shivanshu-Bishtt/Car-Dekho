# Car Dekho

A guided quiz that takes a confused car buyer from *"I don't know what to buy"* to *"I'm confident about my shortlist."*

Instead of dumping a giant filterable catalog on the user, Car Match asks five simple questions, scores every car in the dataset against those answers, and returns a ranked shortlist of the best matches — each with a one-line reason explaining *why* it fits.

**Live app:** _<add your Streamlit URL here once deployed>_

---

## Run it locally (under 2 minutes)

```bash
pip install -r requirements.txt
python database.py        # creates and seeds cars.db (run once)
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## What I built and why

The brief is vague on purpose, so the first decision was scoping. Every car research site already has search and filters — that's not where confused buyers get stuck. They get stuck on **decision paralysis**: too many options and no opinion to anchor on.

So I built the opinionated thing instead of the catalog. **Car Match** is a five-question guided flow (budget, primary use, seats, fuel preference, top priority). The backend runs every car through a weighted scoring engine, applies hard filters (budget and seats), and returns the top 5 matches with a plain-English reason for each, plus a side-by-side comparison table.

The goal was to give the buyer **an answer and the reasoning behind it**, not just more tools to do their own research.

### What I deliberately cut
- **User accounts / login** — adds no value to a single-session decision tool.
- **Review sentiment / NLP** — high effort, and not the core of the "which car" decision in a 2–3 hour window.
- **A large filterable catalog** — explicitly the thing I was avoiding building.
- **Pixel-perfect design** — clean and usable beats polished-but-unfinished.

---

## Tech stack and why

- **Python + Streamlit** for the entire app. One language end-to-end, no separate JS frontend to wire up, and it deploys to Streamlit Community Cloud for free. This let me ship a working full-stack app comfortably inside the time-box.
- **SQLite (Python standard library)** for persistence — zero-config, no DB server, ships as a single file, which keeps local setup trivial.
- **A hand-written scoring engine (`score.py`)** as the core logic, kept as a pure function so it's easy to reason about and tune.

**Architecture:**
- `database.py` — creates and seeds the SQLite database (~40 realistic Indian-market cars), exposes `get_all_cars()`.
- `score.py` — pure `score_cars(cars, prefs)` function: hard filters, weighted 0–100 scoring, returns top 5 with reasons.
- `app.py` — the Streamlit UI: multi-step quiz driven by `st.session_state`, results cards, and a comparison table.

---

## What I delegated to AI tools vs. did manually

I used **Claude Code** inside VS Code throughout, and drove it in clear, separate steps rather than one giant prompt: scaffold the data layer, then the scoring engine, then the UI.

**Delegated to AI:**
- Generating the SQLite schema and the ~40-car seed dataset.
- Boilerplate Streamlit layout and the multi-step session-state flow.
- Git setup and deployment commands.

**Did manually / course-corrected:**
- **Reviewed the seed data** before trusting it — checked prices, body-type variety, and that EV specs weren't nonsense, rather than accepting it blind.
- **Tuned the scoring weights by hand.** The AI's first weighting was reasonable, but for a *confused* buyer, staying within budget is the scariest thing to get wrong — so I bumped budget weight up and trimmed the "use" weight, since the user's stated priority already captures intent.

**Where tools helped most:** scaffolding and boilerplate — the repetitive setup that would have eaten most of the time-box.

**Where they got in the way:** _<replace with your real moment — e.g. "an early file got created empty and I cleaned it up," or any place a prompt produced something I had to redirect>_

---

## If I had another 4 hours

- **Real review signal** — pull in user-review sentiment so the reason line reflects ownership experience, not just specs.
- **An EMI / affordability calculator** so budget reflects monthly payment, not just sticker price.
- **A free-text "describe your ideal car"** entry that maps natural language onto the preference dict (a natural fit for an LLM call).
- **Light tests** on `score_cars` to lock in the filter and ranking behavior.
