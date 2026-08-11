"""
app.py -- Flask server for the Adaptive UI project (MSAI-631-B02).

Endpoints
---------
GET  /            Adaptive dashboard demo page.
POST /api/adapt   Receives live behavioral telemetry from the browser and
                  returns an AI-computed UI adaptation profile.
GET  /api/health  Liveness check.

Author: Vinoth Nageshwaran <vnageshwaran@gmail.com>
"""

import json
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from adaptive_engine import build_adaptation

app = Flask(__name__)
LOG_PATH = os.path.join(os.path.dirname(__file__), "data", "sessions.jsonl")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/adapt")
def adapt():
    payload = request.get_json(force=True, silent=True) or {}
    metrics = payload.get("metrics", {})
    feature_counts = payload.get("feature_counts", {})

    adaptation = build_adaptation(metrics, feature_counts)

    # Append the session snapshot for future model retraining.
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "feature_counts": feature_counts,
            "persona": adaptation["persona"],
        }) + "\n")

    return jsonify(adaptation)


@app.get("/api/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
