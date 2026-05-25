# Delhivery - Optimizing Delivery ETAs with Graph-Based Network Intelligence

> Optimizing Delivery ETAs with Graph-Structural Machine Learning | Summer Project 2026

## Problem Statement

Delhivery's OSRM-based ETA system underestimates delivery time on **86.5% of routes**. This project builds a graph-based intelligent system that produces more accurate ETAs, surfaces bottleneck hubs, and generates actionable recommendations for operations leadership.

## Team

| Member | Role |
|--------|------|
| Surbhi Kumari | Full pipeline — data engineering, graph construction, ML modelling, visualizations, business strategy |

---

## Key Results

| Metric | Baseline | Graph-Enhanced |
|--------|----------|---------------|
| MAE (delay ratio) | 0.6933 | 0.5143 |
| Within-15% accuracy | 31.4% | 46.4% |
| **MAE Improvement** | — | **25.8% ✅** |

Target was 15% MAE improvement — achieved 25.8%.

---

## Project Architecture

```
delhivery_project/
├── delivery_data.csv               # Raw dataset (144K trips)
├── data/
│   └── processed/
│       ├── cleaned_data.csv        # After dedup + feature engineering
│       └── final_data.csv          # + graph centrality features
├── src/
│   ├── data_preprocessing.py       # Pipeline: cleaning, feature engineering
│   ├── graph_builder.py            # Graph construction + centrality analysis
│   ├── model_training.py           # Baseline vs Graph-Enhanced benchmarking
│   ├── ftl_carting_framework.py    # ML-backed FTL decision framework
│   └── visualizations.py          # Network graph + heatmaps + hourly patterns
├── models/
│   ├── baseline_xgb.pkl
│   ├── graph_xgb.pkl
│   ├── benchmark_results.json      # MAE, accuracy, improvement %
│   └── feature_importance.csv
├── visualizations/
│   ├── top5_hubs.json             # Top 5 bottleneck hub data
│   ├── ftl_carting_stats.csv
│   └── output/
│       ├── network_graph.png
│       ├── heatmap_corridor.png
│       ├── hourly_delay_pattern.png
│       └── ftl_carting_analysis.png
├── reports/
│   ├── Delhivery_Presentation.pptx # 8-slide deck with real model results
│   └── Strategy_Memo_Delhivery.docx
├── generate_ppt.js                 # PptxGenJS presentation generator
└── generate_memo.py                # Strategy memo generator
```

---

## Design Decisions & What's Different

### 1. Target variable: `segment_factor`, not raw difference
Using `actual_time / osrm_time` (dimensionless ratio) instead of `actual_time - osrm_time` makes the metric comparable across corridors of different lengths. A 10-minute delay on a 15-minute route is fundamentally different from a 10-minute delay on a 4-hour route.

### 2. Winsorizing outliers
The raw data contains segment_factor values up to 574× (corrupted records or extreme outliers). We winsorize at the 99th percentile (9×) to prevent the model from overfitting to noise.

### 3. Median edge weights in graph
Edge weights in the graph use **median** delay ratio per corridor (not mean). This is robust to the long-tailed distribution observed in the data.

### 4. Rigorous two-model benchmarking
Both baseline and graph-enhanced models are trained on identical train/test splits. The "graph advantage" is measured as % MAE reduction — not claimed.

### 5. ML-backed FTL conversion priority
The FTL decision framework isn't just descriptive statistics — it uses a composite conversion priority score: `delay × sla_breach_rate × (1 + centrality × 100)` to rank Carting corridors for conversion.

---

## How to Run

```bash
# Install dependencies
pip3 install pandas networkx scikit-learn xgboost matplotlib seaborn joblib

# Run pipeline in order
cd delhivery/
python3 src/data_preprocessing.py
python3 src/graph_builder.py
python3 src/model_training.py
python3 src/ftl_carting_framework.py
python3 src/visualizations.py

# Generate reports
python3 generate_memo.py
npm install -g pptxgenjs && node generate_ppt.js
```

---

## Analytics Resources Referenced

- Graph-Based Analytics: [Analytics Vidhya — Graph Theory](https://www.analyticsvidhya.com/blog/2018/04/introduction-to-graph-theory-network-analysis-python-codes/)
- Graph Neural Networks: [GNN Explained — Medium](https://medium.com/data-science-collective/gnn-graph-neural-net-explained-intuition-concepts-applications-7825eea73362)
- NetworkX documentation for betweenness centrality and PageRank
