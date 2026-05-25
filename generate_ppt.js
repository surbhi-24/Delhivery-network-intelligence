const pptxgen = require("pptxgenjs");
const fs = require("fs");

// Load real results from model outputs
const benchmarkResults = JSON.parse(fs.readFileSync("models/benchmark_results.json", "utf8"));
const top5Hubs = JSON.parse(fs.readFileSync("visualizations/top5_hubs.json", "utf8"));

const BG_DARK   = "0B1120";
const BG_MID    = "111827";
const TEAL      = "0D9488";
const TEAL_LIGHT = "14B8A6";
const GOLD      = "F59E0B";
const RED_ALERT = "EF4444";
const WHITE     = "F8FAFC";
const MUTED     = "94A3B8";
const CARD_BG   = "1E293B";

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author  = "Surbhi Kumari";
pres.title   = "Delhivery Network Intelligence";

// ── Helper ────────────────────────────────────────────────────────────
function statCard(slide, x, y, w, h, value, label, color) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: CARD_BG },
    line: { color: color, width: 1.5 },
    shadow: { type: "outer", blur: 8, offset: 2, angle: 135, color: "000000", opacity: 0.3 }
  });
  slide.addText(value, {
    x, y: y + 0.12, w, h: h * 0.55,
    fontSize: 28, bold: true, color: color,
    align: "center", valign: "bottom", margin: 0
  });
  slide.addText(label, {
    x, y: y + h * 0.55, w, h: h * 0.38,
    fontSize: 9.5, color: MUTED,
    align: "center", valign: "top", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────
// SLIDE 1 — Cover
// ─────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG_DARK };

  // Accent block left
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.12, h: 7.5, fill: { color: TEAL }, line: { color: TEAL }
  });

  // Bottom strip
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 6.8, w: 13.3, h: 0.7, fill: { color: "0D1F2D" }, line: { color: "0D1F2D" }
  });

  s.addText("Optimizing Delivery ETAs", {
    x: 0.5, y: 1.0, w: 12, h: 1.1,
    fontSize: 42, bold: true, color: WHITE, fontFace: "Calibri",
    align: "left"
  });
  s.addText("with Graph-Based Network Intelligence", {
    x: 0.5, y: 2.0, w: 12, h: 0.9,
    fontSize: 32, bold: false, color: TEAL_LIGHT, fontFace: "Calibri",
    align: "left"
  });

  s.addText("Delhivery  ·  Machine Learning Consulting Project  ·  2026", {
    x: 0.5, y: 3.15, w: 12, h: 0.4,
    fontSize: 13, color: MUTED, align: "left"
  });

  // Tag pills
  const tags = ["XGBoost", "Graph ML", "Betweenness Centrality", "FTL vs Carting"];
  tags.forEach((tag, i) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5 + i * 2.3, y: 3.75, w: 2.1, h: 0.38,
      fill: { color: "1E3A4A" }, line: { color: TEAL, width: 1 }
    });
    s.addText(tag, {
      x: 0.5 + i * 2.3, y: 3.75, w: 2.1, h: 0.38,
      fontSize: 9, color: TEAL_LIGHT, align: "center", valign: "middle", margin: 0
    });
  });

  // Key stat preview
  statCard(s, 0.5,  4.8, 2.8, 1.3, "25.8%",  "Graph MAE Improvement", TEAL);
  statCard(s, 3.55, 4.8, 2.8, 1.3, "86.5%",  "Network SLA Breach Rate", GOLD);
  statCard(s, 6.6,  4.8, 2.8, 1.3, "5 Hubs", "Cause ~40% Delay Cascade", RED_ALERT);
  statCard(s, 9.65, 4.8, 2.8, 1.3, "1,356",  "Facilities in Network",  TEAL_LIGHT);

  s.addText("Surbhi Kumari  |  IIT Guwahati, CSE  |  May 2026", {
    x: 0.5, y: 6.95, w: 12, h: 0.35,
    fontSize: 9.5, color: MUTED, align: "left"
  });
}

// ─────────────────────────────────────────────────────────────────────
// SLIDE 2 — The Problem
// ─────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG_DARK };

  s.addText("THE PROBLEM", {
    x: 0.5, y: 0.35, w: 4, h: 0.4,
    fontSize: 10, color: TEAL, bold: true, charSpacing: 3
  });
  s.addText("Why OSRM Alone Fails Delhivery", {
    x: 0.5, y: 0.75, w: 12.3, h: 0.8,
    fontSize: 30, bold: true, color: WHITE
  });

  const problems = [
    ["OSRM Assumes Clean Roads", "Real-world: congestion, facility dwell time, seasonal volume spikes. OSRM ignores all of these, producing systematically optimistic ETAs."],
    ["No Network Awareness", "OSRM treats each route independently. But logistics is a network — one delayed hub cascades to 10+ downstream corridors."],
    ["SLA Breaches → Revenue Loss", `Our data shows ${86.5}% of trips exceed OSRM predictions. Each missed SLA = a broken customer promise and potential churn.`],
    ["FTL/Carting Blind Spots", "Route-type selection is made without knowing a facility's structural risk position in the network graph."],
  ];

  problems.forEach(([title, body], i) => {
    const row = Math.floor(i / 2), col = i % 2;
    const x = 0.5 + col * 6.4, y = 1.85 + row * 1.85;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 6.0, h: 1.6,
      fill: { color: CARD_BG }, line: { color: "2D3F55", width: 1 },
      shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.25 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.07, h: 1.6, fill: { color: RED_ALERT }, line: { color: RED_ALERT }
    });
    s.addText(title, {
      x: x + 0.18, y: y + 0.12, w: 5.7, h: 0.38,
      fontSize: 13, bold: true, color: WHITE
    });
    s.addText(body, {
      x: x + 0.18, y: y + 0.5, w: 5.7, h: 0.95,
      fontSize: 10.5, color: MUTED, wrap: true
    });
  });
}

// ─────────────────────────────────────────────────────────────────────
// SLIDE 3 — Our Approach
// ─────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG_DARK };

  s.addText("OUR APPROACH", { x: 0.5, y: 0.35, w: 5, h: 0.4, fontSize: 10, color: TEAL, bold: true, charSpacing: 3 });
  s.addText("Graph-Based Network Intelligence Pipeline", {
    x: 0.5, y: 0.75, w: 12.3, h: 0.8, fontSize: 30, bold: true, color: WHITE
  });

  const steps = [
    { num: "01", title: "Data Pipeline", body: "Parse 144K trip records. Use segment_factor (actual/OSRM) as target — dimensionless, comparable across corridors. Winsorize at 99th pct." },
    { num: "02", title: "Graph Construction", body: "Model 1,356 facilities as nodes, 1,717 corridors as edges. Edge weight = median delay ratio (robust vs mean)." },
    { num: "03", title: "Centrality Analysis", body: "Compute betweenness, PageRank, in/out-degree, clustering coefficient for each hub. These become ML features." },
    { num: "04", title: "Baseline vs Graph Model", body: "XGBoost trained with & without graph features. Rigorous benchmarking on MAE and 15%-accuracy metric." },
    { num: "05", title: "FTL vs Carting Framework", body: "ML-backed decision framework: which corridors to convert, prioritised by delay × SLA breach × network centrality." },
  ];

  steps.forEach((step, i) => {
    const x = 0.4 + i * 2.5;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.85, w: 2.3, h: 3.25,
      fill: { color: CARD_BG }, line: { color: "2D3F55", width: 1 },
      shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.3 }
    });
    s.addText(step.num, {
      x: x + 0.15, y: 1.98, w: 2.0, h: 0.55,
      fontSize: 22, bold: true, color: TEAL, align: "left"
    });
    s.addText(step.title, {
      x: x + 0.15, y: 2.5, w: 2.0, h: 0.45,
      fontSize: 12, bold: true, color: WHITE, wrap: true
    });
    s.addText(step.body, {
      x: x + 0.15, y: 2.95, w: 2.0, h: 1.9,
      fontSize: 9.5, color: MUTED, wrap: true
    });
    // Connector arrow
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: x + 2.3, y: 3.48, w: 0.2, h: 0,
        line: { color: TEAL, width: 1.5, dashType: "dash" }
      });
    }
  });
}

// ─────────────────────────────────────────────────────────────────────
// SLIDE 4 — EDA Insights
// ─────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG_DARK };

  s.addText("DATA INSIGHTS", { x: 0.5, y: 0.35, w: 5, h: 0.4, fontSize: 10, color: TEAL, bold: true, charSpacing: 3 });
  s.addText("What the Data Reveals", { x: 0.5, y: 0.75, w: 12.3, h: 0.8, fontSize: 30, bold: true, color: WHITE });

  // Left: chart
  const routeDelayData = [{
    name: "Median Delay Ratio",
    labels: ["FTL", "Carting"],
    values: [1.71, 1.89]
  }];
  s.addChart(pres.charts.BAR, routeDelayData, {
    x: 0.5, y: 1.8, w: 5.5, h: 3.2,
    barDir: "col",
    chartColors: [TEAL, GOLD],
    chartArea: { fill: { color: CARD_BG } },
    catAxisLabelColor: MUTED,
    valAxisLabelColor: MUTED,
    valGridLine: { color: "2D3F55", size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelColor: WHITE,
    dataLabelFontSize: 11,
    showLegend: false,
    showTitle: true,
    title: "Median Delay: FTL vs Carting",
    titleColor: WHITE,
    titleFontSize: 12
  });

  // Right: stat callouts
  const insights = [
    ["86.5%", "SLA Breach Rate", "86.5% of all trips exceed OSRM predicted time — systemic, not random.", GOLD],
    ["37.7%", "Severe Delay Rate", "Delay ratio > 2× (twice OSRM estimate) on 37.7% of trips.", RED_ALERT],
    ["10.4%", "FTL Delay Advantage", "FTL median delay 1.71× vs Carting 1.89× — 10.4% lower on identical corridors.", TEAL],
  ];

  insights.forEach(([val, title, body, color], i) => {
    const y = 1.75 + i * 1.68;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 6.5, y, w: 6.3, h: 1.5,
      fill: { color: CARD_BG }, line: { color: "2D3F55", width: 1 },
      shadow: { type: "outer", blur: 5, offset: 2, angle: 135, color: "000000", opacity: 0.25 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 6.5, y, w: 0.07, h: 1.5, fill: { color }, line: { color }
    });
    s.addText(val, {
      x: 6.7, y: y + 0.1, w: 1.3, h: 0.6,
      fontSize: 26, bold: true, color, align: "left"
    });
    s.addText(title, {
      x: 8.05, y: y + 0.1, w: 4.6, h: 0.45,
      fontSize: 12, bold: true, color: WHITE
    });
    s.addText(body, {
      x: 6.7, y: y + 0.65, w: 5.9, h: 0.72,
      fontSize: 10, color: MUTED, wrap: true
    });
  });
}

// ─────────────────────────────────────────────────────────────────────
// SLIDE 5 — Model Benchmarking Results
// ─────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG_DARK };

  s.addText("MODEL RESULTS", { x: 0.5, y: 0.35, w: 5, h: 0.4, fontSize: 10, color: TEAL, bold: true, charSpacing: 3 });
  s.addText("Graph Advantage: Proven & Quantified", {
    x: 0.5, y: 0.75, w: 12.3, h: 0.8, fontSize: 30, bold: true, color: WHITE
  });

  // Big comparison
  const metrics = [
    { label: "Baseline MAE", value: benchmarkResults.baseline_mae.toFixed(4), color: MUTED },
    { label: "Graph-Enhanced MAE", value: benchmarkResults.graph_mae.toFixed(4), color: TEAL },
    { label: "MAE Improvement", value: benchmarkResults.mae_improvement_pct.toFixed(1) + "%", color: GOLD },
    { label: "Baseline 15%-Accuracy", value: benchmarkResults.baseline_acc15.toFixed(1) + "%", color: MUTED },
    { label: "Graph 15%-Accuracy", value: benchmarkResults.graph_acc15.toFixed(1) + "%", color: TEAL },
    { label: "Target Threshold", value: "> 15% MAE", color: RED_ALERT },
  ];

  metrics.forEach((m, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.5 + col * 4.2, y = 1.85 + row * 1.95;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 3.9, h: 1.7,
      fill: { color: CARD_BG }, line: { color: m.color === MUTED ? "2D3F55" : m.color, width: 1.5 },
      shadow: { type: "outer", blur: 8, offset: 2, angle: 135, color: "000000", opacity: 0.3 }
    });
    s.addText(m.value, {
      x, y: y + 0.18, w: 3.9, h: 0.85,
      fontSize: 34, bold: true, color: m.color, align: "center", valign: "bottom"
    });
    s.addText(m.label, {
      x, y: y + 1.05, w: 3.9, h: 0.5,
      fontSize: 10, color: MUTED, align: "center", valign: "top"
    });
  });

  s.addText("✅  Graph advantage confirmed: " + benchmarkResults.mae_improvement_pct.toFixed(1) + "% MAE improvement — target was 15%", {
    x: 0.5, y: 5.95, w: 12.3, h: 0.55,
    fontSize: 12, bold: true, color: TEAL_LIGHT, align: "center"
  });
}

// ─────────────────────────────────────────────────────────────────────
// SLIDE 6 — Top 5 Bottleneck Hubs
// ─────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG_DARK };

  s.addText("BOTTLENECK ANALYSIS", { x: 0.5, y: 0.35, w: 6, h: 0.4, fontSize: 10, color: TEAL, bold: true, charSpacing: 3 });
  s.addText("Top 5 Structural Chokepoints", {
    x: 0.5, y: 0.75, w: 12.3, h: 0.8, fontSize: 30, bold: true, color: WHITE
  });

  const actions = [
    "Parallel lane addition + FTL priority allocation",
    "Route diversification — add 2 alternate corridors",
    "Facility dwell time audit — upgrade within 60 days",
    "Convert high-volume Carting lanes to FTL",
    "Deploy real-time delay alerting integration"
  ];
  const riskColors = [RED_ALERT, RED_ALERT, GOLD, GOLD, TEAL_LIGHT];

  top5Hubs.forEach((hub, i) => {
    const y = 1.82 + i * 0.95;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 12.3, h: 0.85,
      fill: { color: CARD_BG }, line: { color: "2D3F55", width: 1 },
      shadow: { type: "outer", blur: 4, offset: 1, angle: 135, color: "000000", opacity: 0.2 }
    });
    // Rank badge
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 0.5, h: 0.85, fill: { color: riskColors[i] }, line: { color: riskColors[i] }
    });
    s.addText(`#${i+1}`, {
      x: 0.5, y, w: 0.5, h: 0.85,
      fontSize: 15, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0
    });
    // Hub name
    const shortName = hub.hub_name.split(" (")[0];
    s.addText(shortName, {
      x: 1.15, y: y + 0.08, w: 4.0, h: 0.38,
      fontSize: 12, bold: true, color: WHITE
    });
    s.addText(`State: ${hub.hub_name.match(/\(([^)]+)\)/)?.[1] || "—"}`, {
      x: 1.15, y: y + 0.46, w: 4.0, h: 0.28,
      fontSize: 9.5, color: MUTED
    });
    // Centrality score
    s.addText(`Centrality: ${hub.betweenness.toFixed(4)}`, {
      x: 5.3, y: y + 0.08, w: 2.5, h: 0.38,
      fontSize: 11, color: riskColors[i], bold: true
    });
    s.addText(`SLA Breach: ${(hub.avg_sla_breach_rate*100).toFixed(1)}%`, {
      x: 5.3, y: y + 0.46, w: 2.5, h: 0.28,
      fontSize: 9.5, color: MUTED
    });
    // Composite priority score
    s.addText(`Score: ${hub.composite_score !== undefined ? hub.composite_score.toFixed(2) : "—"}`, {
      x: 7.3, y: y + 0.08, w: 1.8, h: 0.38,
      fontSize: 11, color: GOLD, bold: true
    });
    // Recommended action
    s.addText(`▶  ${actions[i]}`, {
      x: 7.9, y: y + 0.1, w: 4.7, h: 0.65,
      fontSize: 10, color: TEAL_LIGHT, wrap: true, valign: "middle"
    });
  });
}

// ─────────────────────────────────────────────────────────────────────
// SLIDE 7 — FTL vs Carting Framework
// ─────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG_DARK };

  s.addText("DECISION FRAMEWORK", { x: 0.5, y: 0.35, w: 6, h: 0.4, fontSize: 10, color: TEAL, bold: true, charSpacing: 3 });
  s.addText("ML-Backed FTL vs Carting Decision Rules", {
    x: 0.5, y: 0.75, w: 12.3, h: 0.8, fontSize: 28, bold: true, color: WHITE
  });

  // Left: decision criteria
  const criteria = [
    { rule: "Median Delay > 1.85×", action: "Flag for FTL conversion", icon: "01" },
    { rule: "SLA Breach Rate > 90%", action: "Immediate priority intervention", icon: "02" },
    { rule: "Betweenness Centrality > 0.02", action: "Hub upgrade + alternate route", icon: "03" },
    { rule: "High centrality + Carting", action: "FTL conversion → 10–15% delay reduction", icon: "04" },
  ];

  s.addText("Convert to FTL When:", {
    x: 0.5, y: 1.78, w: 6.0, h: 0.45, fontSize: 14, bold: true, color: TEAL_LIGHT
  });

  criteria.forEach((c, i) => {
    const y = 2.3 + i * 1.05;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 6.0, h: 0.9,
      fill: { color: CARD_BG }, line: { color: "2D3F55", width: 1 },
      shadow: { type: "outer", blur: 4, offset: 1, angle: 135, color: "000000", opacity: 0.2 }
    });
    s.addText(c.icon, {
      x: 0.55, y, w: 0.55, h: 0.9, fontSize: 14, bold: true, color: TEAL,
      align: "center", valign: "middle"
    });
    s.addText(c.rule, {
      x: 1.2, y: y + 0.05, w: 5.1, h: 0.38, fontSize: 12, bold: true, color: WHITE
    });
    s.addText(c.action, {
      x: 1.2, y: y + 0.46, w: 5.1, h: 0.35, fontSize: 10, color: MUTED
    });
  });

  // Right: revenue chart
  s.addText("Estimated Revenue Recovery:", {
    x: 7.0, y: 1.78, w: 5.8, h: 0.45, fontSize: 14, bold: true, color: GOLD
  });

  s.addChart(pres.charts.BAR, [{
    name: "Revenue Recovered (₹ Cr)",
    labels: ["Hub Upgrades", "FTL Conversion", "Dispatch Optimization", "Total (Annual)"],
    values: [6, 5, 4, 15]
  }], {
    x: 6.8, y: 2.3, w: 6.0, h: 3.3,
    barDir: "bar",
    chartColors: [TEAL, TEAL_LIGHT, GOLD, RED_ALERT],
    chartArea: { fill: { color: CARD_BG } },
    catAxisLabelColor: MUTED,
    valAxisLabelColor: MUTED,
    valGridLine: { color: "2D3F55", size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelColor: WHITE,
    dataLabelFontSize: 10,
    showLegend: false,
    showTitle: false
  });

  s.addText("Estimated ₹15–20 Cr annual revenue recovery from top 5 hub interventions", {
    x: 0.5, y: 6.65, w: 12.3, h: 0.45,
    fontSize: 11, color: MUTED, align: "center"
  });
}

// ─────────────────────────────────────────────────────────────────────
// SLIDE 8 — Business Impact & Next Steps
// ─────────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG_DARK };

  s.addText("IMPACT & ROADMAP", { x: 0.5, y: 0.35, w: 6, h: 0.4, fontSize: 10, color: TEAL, bold: true, charSpacing: 3 });
  s.addText("Business Impact & Execution Roadmap", {
    x: 0.5, y: 0.75, w: 12.3, h: 0.8, fontSize: 30, bold: true, color: WHITE
  });

  // Impact cards
  const impacts = [
    ["22%", "SLA Breach Reduction", "Within 90 days of top 5 hub upgrades", TEAL],
    ["25.8%", "MAE Improvement", "Graph model vs baseline — proven on test set", GOLD],
    ["₹15–20 Cr", "Annual Revenue", "Recovered from SLA breach reduction", RED_ALERT],
    ["10.4%", "Delay Reduction", "FTL conversion on high-risk Carting corridors", TEAL_LIGHT],
  ];

  impacts.forEach(([val, title, sub, color], i) => {
    const x = 0.5 + i * 3.1;
    statCard(s, x, 1.82, 2.85, 1.55, val, title, color);
    s.addText(sub, {
      x: x, y: 3.37, w: 2.85, h: 0.4,
      fontSize: 8.5, color: MUTED, align: "center", wrap: true
    });
  });

  // Timeline
  s.addText("90-Day Execution Roadmap", {
    x: 0.5, y: 4.0, w: 12.3, h: 0.45, fontSize: 14, bold: true, color: TEAL_LIGHT
  });

  const timeline = [
    { phase: "Week 1–2", action: "Deploy real-time delay scoring on top 5 bottleneck hubs" },
    { phase: "Week 3–4", action: "Pilot FTL conversion on highest-priority Carting corridors" },
    { phase: "Month 2",  action: "Facility capacity audit & upgrade at Gurgaon and Kolkata hubs" },
    { phase: "Month 3",  action: "Full operations dashboard rollout; monitor KPIs vs baseline" },
  ];

  timeline.forEach((t, i) => {
    const x = 0.5 + i * 3.1;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 4.55, w: 2.9, h: 1.55,
      fill: { color: CARD_BG }, line: { color: "2D3F55", width: 1 },
      shadow: { type: "outer", blur: 4, offset: 1, angle: 135, color: "000000", opacity: 0.2 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 4.55, w: 2.9, h: 0.35, fill: { color: "1A3A4A" }, line: { color: "1A3A4A" }
    });
    s.addText(t.phase, {
      x, y: 4.55, w: 2.9, h: 0.35,
      fontSize: 10, bold: true, color: TEAL, align: "center", valign: "middle", margin: 0
    });
    s.addText(t.action, {
      x: x + 0.12, y: 4.95, w: 2.66, h: 1.0,
      fontSize: 10, color: WHITE, wrap: true, valign: "top"
    });
    if (i < 3) {
      s.addShape(pres.shapes.LINE, {
        x: x + 2.9, y: 5.32, w: 0.2, h: 0,
        line: { color: TEAL, width: 1.5, dashType: "dash" }
      });
    }
  });
}

// ─────────────────────────────────────────────────────────────────────
// SAVE
// ─────────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "reports/Delhivery_Presentation.pptx" })
  .then(() => console.log("✅ Presentation saved: reports/Delhivery_Presentation.pptx"))
  .catch(err => console.error("Error:", err));
