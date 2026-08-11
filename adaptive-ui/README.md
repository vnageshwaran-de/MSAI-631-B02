# Adaptive UI using AI — MSAI-631-B02 Project

**Author:** Vinoth Nageshwaran (vnageshwaran@gmail.com)
**Course:** MSAI-631-B02 — Artificial Intelligence for Human-Computer Interaction, University of the Cumberlands (2026 Summer, Second Bi-term)

A Flask + JavaScript web application demonstrating an **AI-based adaptive user
interface**. The browser continuously collects behavioral telemetry (action
timing, error rate, feature breadth, help usage); a server-side **k-means
clustering model** (scikit-learn) classifies the session into a *novice*,
*intermediate*, or *expert* persona; and the UI adapts in real time.

## Adaptations demonstrated

| Adaptation | Driven by |
|---|---|
| Layout density (comfortable / cozy / compact) | ML persona |
| Font scaling | ML persona |
| Progressive disclosure of advanced tools | ML persona |
| Tooltips & onboarding hints on/off | ML persona |
| Navigation menu reordering | Per-feature usage frequency |
| Light / dark theme | Time-of-day context |
| Transparency panel ("What the AI sees") | Live telemetry + model rationale |

## Project structure

```
adaptive-ui/
├── app.py               # Flask server + /api/adapt endpoint
├── adaptive_engine.py   # k-means persona model + adaptation rules
├── templates/index.html # adaptive dashboard demo
├── static/js/tracker.js # behavioral telemetry collector
├── static/js/adapt.js   # applies AI decisions to the DOM
├── static/css/styles.css# theme/density adaptation hooks
└── data/                # logged sessions (JSONL) for retraining
```

## Run it

```bash
cd adaptive-ui
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

Try behaving like a **novice** (click slowly, make typos in the command box,
press Help) versus an **expert** (click quickly and accurately across many
features) and watch the interface re-shape itself: density, font size, menu
order, hints, and the advanced-tools panel all change, and the side panel
explains the model's decision.

## How the AI works

1. `tracker.js` maintains a rolling window of inter-action times, error and
   help ratios, and distinct-feature breadth.
2. `POST /api/adapt` sends these four normalized metrics to the server.
3. `adaptive_engine.py` standardizes the vector and classifies it with a
   k-means model (k = 3) trained on seed sessions; clusters are labeled by
   mean task speed so ids map to personas deterministically.
4. The persona selects a UI profile; usage frequencies reorder navigation;
   local time selects the theme. The JSON profile is applied client-side.
5. Every session snapshot is appended to `data/sessions.jsonl` so the seed
   data can later be replaced with real logged sessions.
