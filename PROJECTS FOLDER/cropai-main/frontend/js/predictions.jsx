/* CropAI — Predictions, Cultivated Area Calculator, Recommendations & History */
(function () {
  const c = React.createElement;
  const { useState, useEffect } = React;
  const { Icon, Reveal, SectionHead, CountUp, RChart, DATA } = window;

  function Field({ label, icon, hint, children }) {
    return c("div", { className: "field" },
      c("label", null, icon && c(Icon, { name: icon, size: 15, style: { color: "var(--accent-teal)" } }), label, hint && c("span", { className: "req" }, hint)),
      children);
  }

  function Slider({ value, onChange, min, max, step }) {
    return c("div", { className: "slider-row" },
      c("input", { type: "range", className: "range", min, max, step, value, onChange: e => onChange(+e.target.value) }),
      c("input", { type: "number", className: "inp", min, max, step, value, onChange: e => onChange(+e.target.value) }));
  }

  const classifierNames = () => {
    const live = (DATA.CLASSIFIERS || []).map(m => m.name).filter(Boolean);
    return live.length ? live : ["Random Forest Classifier", "K-Nearest Neighbors (k=5)", "Logistic Regression", "Naive Bayes"];
  };

  const defaultRegModel = () => {
    const r = (DATA.REGRESSION || []).filter(m => !m.baseline);
    return ((r.find(m => m.best) || r[0] || {}).name) || "Random Forest";
  };

  function Predictions() {
    const [task, setTask] = useState("regression");   // regression | classification | recommendation
    const [ctype, setCtype] = useState("binary");       // binary | 3class
    const [f, setF] = useState({
      country: "Albania",
      crop: "Maize",
      year: 2010,
      rain: 1485,
      pest: 121,
      temp: 16.4,
      model: "Random Forest",
      farmArea: "",
      farmAreaUnit: "ha",
    });
    const [state, setState] = useState("idle"); // idle | loading | done | error
    const [result, setResult] = useState(null);
    const [history, setHistory] = useState(null);
    const [recResult, setRecResult] = useState(null);
    const [dbHistory, setDbHistory] = useState([]);
    const [dbLoading, setDbLoading] = useState(false);
    const [errMsg, setErrMsg] = useState("");

    const set = (k, v) => setF(p => ({ ...p, [k]: v }));

    // Load persistent history from SQLite backend
    const loadDbHistory = async () => {
      setDbLoading(true);
      try {
        const res = await fetch("/api/history?limit=25");
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data.records)) {
            setDbHistory(data.records);
          }
        }
      } catch (_) { /* optional */ }
      setDbLoading(false);
    };

    useEffect(() => {
      loadDbHistory();
    }, []);

    const clearDbHistory = async () => {
      if (!confirm("Are you sure you want to clear all persistent prediction history?")) return;
      try {
        const res = await fetch("/api/history", { method: "DELETE" });
        if (res.ok) {
          setDbHistory([]);
        }
      } catch (e) {
        alert("Failed to clear history: " + e.message);
      }
    };

    // switch task
    const switchTask = (t) => {
      setTask(t);
      setState("idle");
      setResult(null);
      setRecResult(null);
      setErrMsg("");
      set("model", t === "classification" ? classifierNames()[0] : defaultRegModel());
    };

    const predict = async () => {
      setState("loading");
      setErrMsg("");

      try {
        // ── Recommendation branch (Phase 4) ──
        if (task === "recommendation") {
          const payload = {
            country: f.country,
            year: f.year,
            rain: f.rain,
            pest: f.pest,
            temp: f.temp,
            model: f.model,
            farm_area: f.farmArea ? parseFloat(f.farmArea) : null,
            farm_area_unit: f.farmAreaUnit,
          };
          const res = await fetch("/api/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const r = await res.json();
          if (!res.ok) throw new Error(r.error || "Recommendation failed");
          setRecResult(r);
          setState("done");
          return;
        }

        // ── Classification branch ──
        if (task === "classification") {
          const payload = {
            country: f.country,
            crop: f.crop,
            year: f.year,
            rain: f.rain,
            pest: f.pest,
            temp: f.temp,
            model: f.model,
            type: ctype
          };
          const res = await fetch("/api/classify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const r = await res.json();
          if (!res.ok) throw new Error(r.error || "Classification failed");
          setHistory(null);
          setResult({
            kind: "classification",
            label: r.label,
            cls: r.class,
            ctype: r.type,
            threshold: r.threshold,
            q33: r.q33,
            q67: r.q67,
            model: r.model
          });
          setState("done");
          loadDbHistory();
          return;
        }

        // ── Regression branch (Phase 2 & Phase 3) ──
        const payload = {
          country: f.country,
          crop: f.crop,
          year: f.year,
          rain: f.rain,
          pest: f.pest,
          temp: f.temp,
          model: f.model,
          farm_area: f.farmArea ? parseFloat(f.farmArea) : null,
          farm_area_unit: f.farmAreaUnit,
        };
        const res = await fetch("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const r = await res.json();
        if (!res.ok) throw new Error(r.error || "Prediction failed");

        let hist = null;
        try {
          const hres = await fetch(`/api/history?country=${encodeURIComponent(f.country)}&crop=${encodeURIComponent(f.crop)}`);
          if (hres.ok) {
            const hj = await hres.json();
            if (!hj.empty) hist = hj;
          }
        } catch (_) { /* optional */ }
        setHistory(hist);

        setResult({
          kind: "regression",
          y: Math.round(r.yield),
          yield_tonnes_per_ha: r.yield_tonnes_per_ha,
          farm_area: r.farm_area,
          farm_area_unit: r.farm_area_unit,
          farm_area_ha: r.farm_area_ha,
          total_harvest_tonnes: r.total_harvest_tonnes,
          harvest_calculation_note: r.harvest_calculation_note,
          pct: r.percentDiff,
          above: r.above,
          conf: r.confidence,
          comparable: r.comparables,
          model: r.model,
        });
        setState("done");
        loadDbHistory();

        // Local storage backup
        try {
          const entry = {
            ts: Date.now(),
            country: f.country,
            crop: f.crop,
            yield: Math.round(r.yield),
            status: r.above ? "above" : "below"
          };
          const prev = JSON.parse(localStorage.getItem("cropai:recent") || "[]");
          const next = [entry, ...prev].slice(0, 10);
          localStorage.setItem("cropai:recent", JSON.stringify(next));
          window.dispatchEvent(new CustomEvent("cropai:prediction", { detail: entry }));
        } catch (_) { /* optional */ }

      } catch (e) {
        setErrMsg(e.message || "Operation failed");
        setState("error");
      }
    };

    return c("div", null,
      c(SectionHead, {
        crumb: ["Home", "Predictions"],
        title: "Predict & Optimize Crop Yield",
        sub: "Machine learning decision support: exact yield, land harvest estimator, categorization & crop recommendation"
      }),

      // MAIN WORKSPACE
      c("div", { className: "grid", style: { gridTemplateColumns: "minmax(0,1.05fr) minmax(0,0.95fr)", gap: 24, alignItems: "start" } },
        // LEFT — Form
        c(Reveal, { i: 0, className: "grad-border" },
          c("h3", { className: "card-title", style: { marginBottom: 14 } }, "Scenario Inputs"),

          // Task switcher tabs
          c("div", { className: "tabs", style: { marginBottom: 18 } },
            c("button", {
              className: "tab" + (task === "regression" ? " active" : ""),
              onClick: () => switchTask("regression")
            }, "📈 Yield Prediction"),
            c("button", {
              className: "tab" + (task === "classification" ? " active" : ""),
              onClick: () => switchTask("classification")
            }, "🏷️ Classification"),
            c("button", {
              className: "tab" + (task === "recommendation" ? " active" : ""),
              onClick: () => switchTask("recommendation")
            }, "🌱 Recommend Crop")),

          // Geographic & Climate Inputs
          c(Field, { label: "Country (Area)", icon: "mapPin" },
            c("select", { className: "inp", value: f.country, onChange: e => set("country", e.target.value) },
              DATA.COUNTRIES.map(x => c("option", { key: x, value: x }, x)))),

          task !== "recommendation" && c(Field, { label: "Crop Type", icon: "wheat" },
            c("select", { className: "inp", value: f.crop, onChange: e => set("crop", e.target.value) },
              DATA.CROPS.map(x => c("option", { key: x, value: x }, x)))),

          c(Field, { label: "Year", icon: "calendar" },
            c("input", { type: "number", className: "inp", min: 1990, max: 2030, value: f.year, onChange: e => set("year", +e.target.value) })),

          c(Field, { label: "Average Rainfall", icon: "droplet", hint: f.rain + " mm/yr" },
            c(Slider, { value: f.rain, onChange: v => set("rain", v), min: 0, max: 5000, step: 1 })),

          c(Field, { label: "Pesticides Used", icon: "flask", hint: DATA.fmt(f.pest) + " tonnes" },
            c(Slider, { value: f.pest, onChange: v => set("pest", v), min: 0, max: 500000, step: 1 })),

          c(Field, { label: "Average Temperature", icon: "thermo", hint: f.temp + " °C" },
            c(Slider, { value: f.temp, onChange: v => set("temp", v), min: -10, max: 50, step: 0.1 })),

          // Phase 2: Cultivated Land Area & Total Harvest Calculator input
          task !== "classification" && c(Field, {
            label: "Cultivated Farm Land Area (Optional)",
            icon: "database",
            hint: "For total harvest calculation"
          },
            c("div", { style: { display: "flex", gap: 8 } },
              c("input", {
                type: "number",
                step: "any",
                min: "0.01",
                placeholder: "e.g. 5.0",
                className: "inp",
                style: { flex: 2 },
                value: f.farmArea,
                onChange: e => set("farmArea", e.target.value)
              }),
              c("select", {
                className: "inp",
                style: { flex: 1.2 },
                value: f.farmAreaUnit,
                onChange: e => set("farmAreaUnit", e.target.value)
              },
                c("option", { value: "ha" }, "Hectares (ha)"),
                c("option", { value: "acres" }, "Acres (ac)")))),

          // Classification category selector
          task === "classification" && c(Field, { label: "Category Type" },
            c("div", { className: "tabs" },
              c("button", { className: "tab" + (ctype === "binary" ? " active" : ""), onClick: () => setCtype("binary") }, "Binary (Above / Below Avg)"),
              c("button", { className: "tab" + (ctype === "3class" ? " active" : ""), onClick: () => setCtype("3class") }, "3-Class (Low / Med / High)"))),

          // Error alert if validation failed
          errMsg && c("div", {
            style: {
              background: "#FFEBEE",
              border: "1px solid #FFCDD2",
              color: "#C62828",
              padding: "10px 14px",
              borderRadius: "8px",
              fontSize: "13px",
              marginTop: 12,
              display: "flex",
              alignItems: "center",
              gap: 8
            }
          },
            c(Icon, { name: "info", size: 16 }),
            c("span", null, errMsg)),

          // Action button
          c("button", {
            className: "btn btn-primary",
            style: { width: "100%", justifyContent: "center", marginTop: 14, padding: "14px" },
            onClick: predict,
            disabled: state === "loading"
          },
            state === "loading"
              ? c(React.Fragment, null, c("span", { className: "spinner" }), "Evaluating Scenario…")
              : c(React.Fragment, null,
                  c(Icon, { name: "sparkles", size: 18 }),
                  task === "classification" ? "Classify Yield Category" : task === "recommendation" ? "Recommend Best Crops" : "Predict Yield & Harvest"))),

        // RIGHT — Result Cards
        c("div", { style: { display: "flex", flexDirection: "column", gap: 24 } },
          task === "recommendation"
            ? c(RecommendationResultCard, { state, recResult, f })
            : c(ResultCard, { state, result, f, errMsg }),

          // Advisory bullet points
          state === "done" && task !== "recommendation" && c(Reveal, { className: "card card-pad" },
            c("h3", { className: "card-title", style: { marginBottom: 12 } }, "Agronomic Assessment"),
            c("ul", { className: "rec-list" },
              [["🌾", `Estimated yield potential for ${f.crop} in ${f.country} under ${f.year} reference climate.`],
               ["💧", `Annual rainfall (${f.rain} mm) is ${f.rain >= 800 && f.rain <= 2000 ? "well-aligned with standard growing cycles" : "dry or heavy; consider irrigation management"}.`],
               ["🌡️", `Average temperature (${f.temp}°C) is ${Math.abs(f.temp - 19) < 7 ? "within temperate vegetative equilibrium" : "potentially causing thermal stress depending on crop variety"}.`],
               ["🧪", `Pesticide usage: ${DATA.fmt(f.pest)} tonnes reported for this national observation.`]].map((r, i) =>
                c("li", { key: i }, c("span", { className: "rico" }, r[0]), c("span", null, r[1])))))
        )
      ),

      // HISTORICAL CHART (when regression is active and done)
      state === "done" && task === "regression" && c("div", { className: "grid g-2", style: { marginTop: 24 } },
        c(Reveal, { className: "card card-pad" },
          c("h3", { className: "card-title", style: { marginBottom: 14 } }, "Input Scenario Summary"),
          c("table", { className: "data" }, c("tbody", null,
            [
              ["Country (Area)", f.country],
              ["Crop Type", f.crop],
              ["Year", f.year],
              ["Rainfall", f.rain + " mm/yr"],
              ["Pesticides", DATA.fmt(f.pest) + " tonnes"],
              ["Temperature", f.temp + " °C"],
              ["Cultivated Area", f.farmArea ? `${f.farmArea} ${f.farmAreaUnit}` : "Not specified (Yield rate only)"]
            ].map(([k, v]) =>
              c("tr", { key: k },
                c("td", { style: { color: "var(--text-muted)" } }, k),
                c("td", { className: "strong", style: { textAlign: "right" } }, String(v))))))),

        c(Reveal, { className: "card card-pad" },
          c("h3", { className: "card-title", style: { marginBottom: 14 } }, `Historical Yield Trend · ${f.country} × ${f.crop}`),
          (() => {
            const histYears = history ? history.years : DATA.HIST_COMBO.years;
            const histVals  = history ? history.yields : DATA.HIST_COMBO.vals;
            const predYear  = f.year;
            return c(RChart, {
              type: "line", height: 280,
              data: {
                labels: histYears,
                datasets: [
                  {
                    label: "Historical Actual",
                    data: histVals,
                    borderColor: "#2E7D32",
                    borderWidth: 2.5,
                    tension: 0.4,
                    pointRadius: 0,
                    fill: true,
                    backgroundColor: ctx => {
                      const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 280);
                      g.addColorStop(0, "rgba(76,175,80,0.25)");
                      g.addColorStop(1, "rgba(76,175,80,0)");
                      return g;
                    }
                  },
                  {
                    label: "Predicted Scenario",
                    data: histYears.map(y => y === predYear && result && result.kind === "regression" ? result.y : null),
                    borderColor: "#00ACC1",
                    pointBackgroundColor: "#00ACC1",
                    pointRadius: 7,
                    pointHoverRadius: 9,
                    showLine: false
                  },
                ]
              },
              options: {
                plugins: {
                  legend: { position: "top", align: "end" },
                  tooltip: { callbacks: { label: x => x.dataset.label + ": " + DATA.fmt(x.raw) + " hg/ha" } }
                },
                scales: {
                  x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
                  y: { grid: RChart.grid, ticks: { callback: v => (v / 1000) + "k" } }
                }
              },
            });
          })())
      ),

      // PHASE 3: PERSISTENT SQLITE PREDICTION HISTORY TABLE
      c("div", { className: "card card-pad", style: { marginTop: 32 } },
        c("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 16 } },
          c("div", null,
            c("h3", { className: "card-title" }, "Persistent Prediction History (SQLite)"),
            c("p", { style: { fontSize: 13, color: "var(--text-muted)", marginTop: 2 } },
              "Saved directly in SQLite database (cropai_history.db). Persists across server restarts and browser reloads.")),
          c("div", { style: { display: "flex", gap: 10 } },
            c("button", {
              className: "btn btn-light",
              style: { padding: "8px 14px", fontSize: 13 },
              onClick: loadDbHistory,
              disabled: dbLoading
            }, c(Icon, { name: "workflow", size: 14 }), dbLoading ? "Refreshing…" : "Refresh"),
            c("a", {
              href: "/api/history/export",
              download: "cropai_history.csv",
              className: "btn btn-ghost",
              style: { padding: "8px 14px", fontSize: 13, textDecoration: "none" }
            }, c(Icon, { name: "database", size: 14 }), "Export CSV"),
            dbHistory.length > 0 && c("button", {
              className: "btn btn-ghost",
              style: { padding: "8px 14px", fontSize: 13, color: "#D32F2F" },
              onClick: clearDbHistory
            }, "Clear History"))),

        dbHistory.length === 0
          ? c("div", { style: { textAlign: "center", padding: "32px 16px", color: "var(--text-muted)" } },
              c(Icon, { name: "database", size: 32, style: { opacity: 0.5, marginBottom: 8 } }),
              c("p", null, "No predictions saved in SQLite database yet. Run a prediction or classification above to record history."))
          : c("div", { style: { overflowX: "auto" } },
              c("table", { className: "data", style: { width: "100%", fontSize: 13 } },
                c("thead", null,
                  c("tr", null,
                    c("th", { style: { textAlign: "left" } }, "#"),
                    c("th", { style: { textAlign: "left" } }, "Timestamp (UTC)"),
                    c("th", { style: { textAlign: "left" } }, "Task"),
                    c("th", { style: { textAlign: "left" } }, "Country & Crop"),
                    c("th", { style: { textAlign: "right" } }, "Climate Inputs"),
                    c("th", { style: { textAlign: "right" } }, "Predicted Yield"),
                    c("th", { style: { textAlign: "right" } }, "Farm Size"),
                    c("th", { style: { textAlign: "right" } }, "Total Harvest"))),
                c("tbody", null,
                  dbHistory.map(row =>
                    c("tr", { key: row.id },
                      c("td", { className: "strong" }, "#" + row.id),
                      c("td", { style: { color: "var(--text-muted)" } }, row.timestamp),
                      c("td", null,
                        c("span", {
                          className: "badge " + (row.task_type === "regression" ? "badge-best" : "badge-above"),
                          style: { fontSize: 11, padding: "2px 8px" }
                        }, row.task_type)),
                      c("td", { className: "strong" }, `${row.country} · ${row.crop}`),
                      c("td", { style: { textAlign: "right", color: "var(--text-muted)" } },
                        `${row.rainfall}mm · ${row.temperature}°C · ${row.pesticides}t`),
                      c("td", { style: { textAlign: "right" } },
                        row.task_type === "regression"
                          ? c("span", { className: "strong" }, DATA.fmt(Math.round(row.predicted_yield)) + " hg/ha")
                          : c("span", { className: "badge badge-above", style: { fontSize: 11 } }, row.classification_label || ("Class " + row.classification_class))),
                      c("td", { style: { textAlign: "right", color: "var(--text-muted)" } },
                        row.farm_area ? `${row.farm_area} ${row.farm_area_unit}` : "—"),
                      c("td", { style: { textAlign: "right", fontWeight: 700, color: "var(--primary-dark)" } },
                        row.total_harvest_tonnes != null ? `${row.total_harvest_tonnes} t` : "—"))))))
      )
    );
  }

  // ── ResultCard for Regression & Classification ──
  function ResultCard({ state, result, f, errMsg }) {
    if (state === "idle") return c("div", { className: "result-card" },
      c("div", { className: "result-empty" },
        c("div", { className: "orb" }, c(Icon, { name: "sparkles", size: 38 })),
        c("p", { style: { maxWidth: 260 } }, "Adjust input parameters and click button to run live yield forecast.")));

    if (state === "loading") return c("div", { className: "result-card" },
      c("div", { className: "result-empty" },
        c("span", { className: "spinner big" }),
        c("p", null, "Evaluating agricultural scenario parameters…")));

    if (state === "error") return c("div", { className: "result-card" },
      c("div", { className: "result-empty" },
        c("div", { className: "orb", style: { background: "rgba(229,57,53,0.12)", color: "#E53935" } }, c(Icon, { name: "info", size: 38 })),
        c("p", { style: { color: "#C62828", fontWeight: 600 } }, errMsg || "Inference error occurred. Check backend logs.")));

    // Classification Result
    if (result && result.kind === "classification") {
      const tone = result.ctype === "binary"
        ? (result.cls === 1 ? "badge-above" : "badge-below")
        : (result.cls === 2 ? "badge-above" : result.cls === 0 ? "badge-below" : "");
      const emoji = result.ctype === "binary"
        ? (result.cls === 1 ? "🌱" : "🍂")
        : (result.cls === 2 ? "🌱" : result.cls === 1 ? "🌾" : "🍂");
      const band = result.ctype === "binary"
        ? `Split at dataset mean ≈ ${DATA.fmt(Math.round(result.threshold))} hg/ha`
        : `Low < ${DATA.fmt(Math.round(result.q33))} · High > ${DATA.fmt(Math.round(result.q67))} hg/ha`;

      return c("div", { className: "result-card live" },
        c("span", { className: "pill", style: { background: "var(--bg-soft)", color: "var(--primary-dark)" } }, "🏷️ Classification Output"),
        c("div", { style: { marginTop: 18 } },
          c("div", { className: "big-metric", style: { fontSize: 36 } }, emoji + " " + result.label),
          c("div", { style: { color: "var(--text-secondary)", marginTop: 8, fontSize: 14 } }, band)),
        c("div", { style: { marginTop: 16 } },
          c("span", { className: "badge " + tone, style: { fontSize: 14, padding: "7px 14px" } }, "Predicted Category: " + result.label)),
        c("div", { className: "inline-stats" },
          c("div", { className: "is" }, c("div", { className: "k" }, "Target Type"), c("div", { className: "v", style: { fontSize: 14 } }, result.ctype === "binary" ? "Binary" : "3-Class")),
          c("div", { className: "is" }, c("div", { className: "k" }, "Database"), c("div", { className: "v", style: { fontSize: 14, color: "var(--primary)" } }, "Saved ✓"))));
    }

    // Regression Result + Cultivated Area Harvest Calculator
    const hasFarmArea = result.total_harvest_tonnes != null;

    return c("div", { className: "result-card live" },
      c("span", { className: "pill", style: { background: "var(--bg-soft)", color: "var(--primary-dark)" } }, "✨ Yield & Harvest Prediction"),
      c("div", { style: { marginTop: 18 } },
        c("div", { className: "big-metric" }, c(CountUp, { value: result.y, suffix: " hg/ha" })),
        c("div", { style: { color: "var(--text-secondary)", marginTop: 8, fontSize: 15 } },
          "Yield Rate: ", c("strong", null, result.yield_tonnes_per_ha != null ? (result.yield_tonnes_per_ha).toFixed(4) : (result.y / 10000000).toFixed(4)), " tonnes / hectare")),

      // Harvest section if farm area provided
      hasFarmArea && c("div", {
        style: {
          marginTop: 20,
          background: "linear-gradient(135deg, rgba(76,175,80,0.12), rgba(0,172,193,0.12))",
          border: "1px solid rgba(76,175,80,0.3)",
          borderRadius: "12px",
          padding: "16px"
        }
      },
        c("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "baseline" } },
          c("span", { style: { fontSize: 12, textTransform: "uppercase", fontWeight: 700, color: "var(--primary-dark)", letterSpacing: "0.05em" } }, "🌾 Total Estimated Harvest"),
          c("span", { style: { fontSize: 13, color: "var(--text-secondary)" } }, `${result.farm_area} ${result.farm_area_unit} (≈ ${result.farm_area_ha} ha)`)),
        c("div", { style: { fontSize: 32, fontWeight: 800, color: "var(--primary-dark)", marginTop: 6 } },
          result.total_harvest_tonnes, " Metric Tonnes"),
        c("div", { style: { fontSize: 12, color: "var(--text-muted)", marginTop: 6, lineHeight: 1.4 } },
          "Calculated: Yield (tonnes/ha) × Land Area (ha). 1 tonne = 10,000,000 hg · 1 ha ≈ 2.47105 acres.")),

      c("div", { style: { marginTop: 16 } },
        c("span", { className: "badge " + (result.above ? "badge-above" : "badge-below"), style: { fontSize: 14, padding: "7px 14px" } },
        result.above ? "🌱 Above Global Average" : "🍂 Below Global Average",
        c("span", { style: { opacity: .8, marginLeft: 6 } }, (result.pct >= 0 ? "+" : "") + result.pct.toFixed(1) + "% vs Mean"))),

      c("div", { className: "inline-stats" },
        c("div", { className: "is" }, c("div", { className: "k" }, "Confidence Score"), c("div", { className: "v" }, result.conf + "%")),
        c("div", { className: "is" }, c("div", { className: "k" }, "SQLite DB"), c("div", { className: "v", style: { fontSize: 13, color: "var(--primary)" } }, "Saved ✓"))));
  }

  // ── RecommendationResultCard for Phase 4 ──
  function RecommendationResultCard({ state, recResult, f }) {
    if (state === "idle") return c("div", { className: "result-card" },
      c("div", { className: "result-empty" },
        c("div", { className: "orb" }, c(Icon, { name: "wheat", size: 38 })),
        c("p", { style: { maxWidth: 260 } }, "Click 'Recommend Best Crops' to evaluate all 10 supported crops for your climate conditions.")));

    if (state === "loading") return c("div", { className: "result-card" },
      c("div", { className: "result-empty" },
        c("span", { className: "spinner big" }),
        c("p", null, "Evaluating yield potential across all 10 agricultural crops…")));

    if (!recResult || !recResult.recommendations) return null;

    const medals = ["🥇", "🥈", "🥉"];

    return c("div", { className: "result-card live" },
      c("span", { className: "pill", style: { background: "var(--bg-soft)", color: "var(--primary-dark)" } }, "🌱 Top Recommended Crops"),
      c("h3", { style: { marginTop: 14, fontSize: 20 } }, `Rankings for ${recResult.country} (${recResult.year})`),

      // Top 3 Cards
      c("div", { style: { display: "flex", flexDirection: "column", gap: 10, marginTop: 14 } },
        recResult.recommendations.map((rec, i) =>
          c("div", {
            key: rec.crop,
            style: {
              background: i === 0 ? "linear-gradient(135deg, rgba(76,175,80,0.15), rgba(76,175,80,0.05))" : "#F8F9FA",
              border: i === 0 ? "1px solid var(--primary)" : "1px solid var(--border)",
              borderRadius: "10px",
              padding: "12px 16px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }
          },
            c("div", { style: { display: "flex", alignItems: "center", gap: 10 } },
              c("span", { style: { fontSize: 22 } }, medals[i]),
              c("div", null,
                c("strong", { style: { fontSize: 16, color: "var(--text-primary)" } }, rec.crop),
                rec.total_harvest_tonnes != null && c("div", { style: { fontSize: 12, color: "var(--primary-dark)", fontWeight: 600 } },
                  `Total Harvest: ${rec.total_harvest_tonnes} tonnes on ${recResult.farm_area} ${recResult.farm_area_unit}`))),
            c("div", { style: { textAlign: "right" } },
              c("div", { style: { fontSize: 16, fontWeight: 700, color: "var(--primary-dark)" } },
                DATA.fmt(Math.round(rec.predicted_yield)) + " hg/ha"),
              c("div", { style: { fontSize: 12, color: "var(--text-muted)" } },
                `≈ ${(rec.yield_tonnes_per_ha).toFixed(3)} t/ha`))))),

      // Disclaimer
      c("div", {
        style: {
          marginTop: 18,
          padding: "10px 14px",
          background: "#FFF8E1",
          border: "1px solid #FFE082",
          borderRadius: "8px",
          fontSize: "12px",
          color: "#795548",
          lineHeight: 1.4
        }
      },
        c("strong", null, "Notice: "), recResult.disclaimer)
    );
  }

  window.Predictions = Predictions;
})();
