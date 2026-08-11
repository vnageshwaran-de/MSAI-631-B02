"""
adaptive_engine.py
------------------
AI engine for the Adaptive UI project (MSAI-631-B02).

Uses unsupervised machine learning (k-means clustering, scikit-learn) to
classify the current user into a proficiency persona (novice, intermediate,
expert) from live behavioral telemetry, then maps that persona -- plus
per-feature usage frequencies and context (time of day) -- to a concrete
UI adaptation profile that the front end applies in real time.

Behavioral feature vector (normalized):
    1. avg_task_time     - mean seconds between meaningful actions (hesitation)
    2. error_rate        - invalid/undone actions per action
    3. feature_breadth   - fraction of distinct features used
    4. help_usage        - help/tooltip opens per action

Author: Vinoth Nageshwaran <vnageshwaran@gmail.com>
Course: MSAI-631-B02 - Artificial Intelligence for Human-Computer Interaction
"""

from datetime import datetime

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# 1. Train the persona model on synthetic seed sessions.
#    Each row: [avg_task_time(s), error_rate, feature_breadth, help_usage]
#    In production this seed data would be replaced/augmented with logged
#    sessions; the pipeline (scale -> cluster -> classify) stays identical.
# ---------------------------------------------------------------------------

_SEED_SESSIONS = np.array([
    # --- novice-like sessions: slow, error-prone, narrow use, lots of help
    [12.0, 0.30, 0.20, 0.40], [10.5, 0.25, 0.25, 0.35], [14.0, 0.35, 0.15, 0.50],
    [11.0, 0.28, 0.22, 0.30], [13.2, 0.32, 0.18, 0.45], [9.8,  0.22, 0.30, 0.28],
    # --- intermediate sessions
    [6.0, 0.12, 0.50, 0.12], [5.5, 0.10, 0.55, 0.10], [7.0, 0.15, 0.45, 0.15],
    [6.5, 0.11, 0.52, 0.08], [5.8, 0.13, 0.48, 0.11], [6.2, 0.09, 0.58, 0.09],
    # --- expert sessions: fast, accurate, broad use, no help
    [2.0, 0.03, 0.85, 0.01], [1.8, 0.02, 0.90, 0.00], [2.5, 0.04, 0.80, 0.02],
    [2.2, 0.03, 0.88, 0.01], [1.9, 0.05, 0.82, 0.00], [2.8, 0.04, 0.78, 0.03],
])

_scaler = StandardScaler().fit(_SEED_SESSIONS)
_model = KMeans(n_clusters=3, n_init=10, random_state=42).fit(
    _scaler.transform(_SEED_SESSIONS)
)

# Label clusters by mean task time so cluster ids map to human-readable
# personas regardless of k-means' arbitrary ordering.
_cluster_speed = [
    _SEED_SESSIONS[_model.labels_ == c][:, 0].mean() for c in range(3)
]
_order = np.argsort(_cluster_speed)          # fastest first
_PERSONA_BY_CLUSTER = {
    int(_order[0]): "expert",
    int(_order[1]): "intermediate",
    int(_order[2]): "novice",
}


def classify_user(metrics: dict) -> str:
    """Classify a live session into a persona with the trained k-means model."""
    vector = np.array([[
        float(metrics.get("avg_task_time", 8.0)),
        float(metrics.get("error_rate", 0.2)),
        float(metrics.get("feature_breadth", 0.3)),
        float(metrics.get("help_usage", 0.2)),
    ]])
    cluster = int(_model.predict(_scaler.transform(vector))[0])
    return _PERSONA_BY_CLUSTER[cluster]


# ---------------------------------------------------------------------------
# 2. Map persona + feature frequencies + context to a UI adaptation profile.
# ---------------------------------------------------------------------------

_PROFILES = {
    "novice": dict(
        density="comfortable", font_scale=1.15, show_tooltips=True,
        show_advanced=False, confirm_destructive=True, onboarding_hints=True,
    ),
    "intermediate": dict(
        density="cozy", font_scale=1.0, show_tooltips=True,
        show_advanced=True, confirm_destructive=True, onboarding_hints=False,
    ),
    "expert": dict(
        density="compact", font_scale=0.92, show_tooltips=False,
        show_advanced=True, confirm_destructive=False, onboarding_hints=False,
    ),
}


def _adaptive_menu_order(feature_counts: dict, default_order: list) -> list:
    """Reorder navigation by observed usage frequency (stable for ties)."""
    return sorted(
        default_order,
        key=lambda f: (-feature_counts.get(f, 0), default_order.index(f)),
    )


def _contextual_theme(hour: int | None = None) -> str:
    """Time-of-day contextual adaptation: dark theme in the evening."""
    hour = datetime.now().hour if hour is None else hour
    return "dark" if (hour >= 19 or hour < 7) else "light"


DEFAULT_FEATURES = ["dashboard", "reports", "analytics", "export", "settings", "help"]


def build_adaptation(metrics: dict, feature_counts: dict,
                     hour: int | None = None) -> dict:
    """Return the full adaptation payload consumed by the front end."""
    persona = classify_user(metrics)
    profile = dict(_PROFILES[persona])
    profile.update(
        persona=persona,
        theme=_contextual_theme(hour),
        menu_order=_adaptive_menu_order(feature_counts, DEFAULT_FEATURES),
        rationale=(
            f"k-means assigned this session to the '{persona}' cluster from "
            f"avg_task_time={metrics.get('avg_task_time', 0):.1f}s, "
            f"error_rate={metrics.get('error_rate', 0):.2f}, "
            f"feature_breadth={metrics.get('feature_breadth', 0):.2f}, "
            f"help_usage={metrics.get('help_usage', 0):.2f}"
        ),
    )
    return profile
