/**
 * tracker.js — client-side behavioral telemetry for the Adaptive UI project.
 * Records action timing, errors, feature usage and help requests, and
 * exposes the normalized metrics the server-side ML model consumes.
 *
 * Author: Vinoth Nageshwaran <vnageshwaran@gmail.com>
 */
window.Tracker = (() => {
  const state = {
    actionTimes: [],       // seconds between meaningful actions
    lastAction: null,
    actions: 0,
    errors: 0,
    helpOpens: 0,
    featureCounts: {},     // feature id -> click count
  };

  const ALL_FEATURES = ["dashboard", "reports", "analytics", "export", "settings", "help"];

  function markAction() {
    const now = performance.now();
    if (state.lastAction !== null) {
      state.actionTimes.push((now - state.lastAction) / 1000);
      if (state.actionTimes.length > 20) state.actionTimes.shift(); // rolling window
    }
    state.lastAction = now;
    state.actions += 1;
  }

  function recordFeature(id) {
    markAction();
    state.featureCounts[id] = (state.featureCounts[id] || 0) + 1;
    if (id === "help") state.helpOpens += 1;
  }

  function recordError() {
    markAction();
    state.errors += 1;
  }

  function metrics() {
    const avg = state.actionTimes.length
      ? state.actionTimes.reduce((a, b) => a + b, 0) / state.actionTimes.length
      : 8.0; // neutral prior before we have data
    const used = ALL_FEATURES.filter(f => state.featureCounts[f]).length;
    return {
      avg_task_time: Math.min(avg, 30),
      error_rate: state.actions ? state.errors / state.actions : 0.2,
      feature_breadth: used / ALL_FEATURES.length,
      help_usage: state.actions ? state.helpOpens / state.actions : 0.2,
    };
  }

  return {
    recordFeature,
    recordError,
    markAction,
    metrics,
    featureCounts: () => ({ ...state.featureCounts }),
    enoughData: () => state.actions >= 3,
  };
})();
