/**
 * adapt.js — applies the AI-computed adaptation profile to the live DOM.
 * Polls POST /api/adapt with current telemetry; the server's k-means model
 * returns persona, theme, density, font scale, tooltip/advanced visibility
 * and a frequency-ranked menu order.
 *
 * Author: Vinoth Nageshwaran <vnageshwaran@gmail.com>
 */
(() => {
  const nav = document.getElementById("main-nav");
  const badge = document.getElementById("persona-badge");
  const rationale = document.getElementById("rationale");
  const advanced = document.getElementById("advanced");
  const hint = document.getElementById("hint");
  const input = document.getElementById("task-input");
  const feedback = document.getElementById("task-feedback");

  const LABELS = {
    dashboard: "Dashboard", reports: "Reports", analytics: "Analytics",
    export: "Export", settings: "Settings", help: "Help",
  };

  // ---- wire up interaction tracking -------------------------------------
  document.querySelectorAll("button.feature").forEach(btn => {
    btn.addEventListener("click", () => {
      Tracker.recordFeature(btn.dataset.feature);
      requestAdaptation();
    });
  });

  input.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    if (input.value.trim().toLowerCase() === "run q3 report") {
      Tracker.recordFeature("reports");
      feedback.textContent = "Report queued ✔";
      feedback.className = "ok";
    } else {
      Tracker.recordError();
      feedback.textContent = "Unrecognized command — counted as an error.";
      feedback.className = "err";
    }
    input.value = "";
    requestAdaptation();
  });

  // ---- render helpers ----------------------------------------------------
  function renderNav(order, showTooltips) {
    nav.innerHTML = "";
    order.forEach(f => {
      const a = document.createElement("button");
      a.className = "nav-item feature";
      a.dataset.feature = f;
      a.textContent = LABELS[f] || f;
      if (showTooltips) a.title = `Open ${LABELS[f] || f}`;
      a.addEventListener("click", () => {
        Tracker.recordFeature(f);
        requestAdaptation();
      });
      nav.appendChild(a);
    });
  }

  function renderMetrics(m) {
    document.getElementById("m-task").textContent = m.avg_task_time.toFixed(1) + " s";
    document.getElementById("m-err").textContent = (m.error_rate * 100).toFixed(0) + " %";
    document.getElementById("m-breadth").textContent = (m.feature_breadth * 100).toFixed(0) + " %";
    document.getElementById("m-help").textContent = (m.help_usage * 100).toFixed(0) + " %";
  }

  function applyProfile(p) {
    const root = document.documentElement;
    root.dataset.theme = p.theme;
    root.dataset.density = p.density;
    root.style.setProperty("--font-scale", p.font_scale);
    badge.textContent = p.persona;
    badge.dataset.persona = p.persona;
    advanced.hidden = !p.show_advanced;
    hint.hidden = !p.onboarding_hints;
    rationale.textContent = p.rationale;
    renderNav(p.menu_order, p.show_tooltips);
  }

  // ---- adaptation loop ---------------------------------------------------
  let inflight = false;
  async function requestAdaptation() {
    const m = Tracker.metrics();
    renderMetrics(m);
    if (!Tracker.enoughData() || inflight) return;
    inflight = true;
    try {
      const res = await fetch("/api/adapt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ metrics: m, feature_counts: Tracker.featureCounts() }),
      });
      if (res.ok) applyProfile(await res.json());
    } catch (err) {
      console.error("adaptation request failed", err);
    } finally {
      inflight = false;
    }
  }

  renderNav(["dashboard", "reports", "analytics", "export", "settings", "help"], true);
  renderMetrics(Tracker.metrics());
  setInterval(requestAdaptation, 8000); // periodic re-evaluation
})();
