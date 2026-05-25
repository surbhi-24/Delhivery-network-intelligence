"""
model_training.py
Delhivery Network Intelligence — Baseline vs Graph-Enhanced Model Benchmarking

Key difference from a naive approach: we train TWO models and measure the
"graph advantage" rigorously — this is what the problem statement requires.

Model 1 (Baseline):  Only trip-level features (no graph structure)
Model 2 (Graph-Enhanced): Adds graph centrality features

We report:
  - MAE on test set (both models)
  - % of predictions within 15% of actual (both models)
  - Feature importance
"""

import pandas as pd
import numpy as np
import joblib
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

df = pd.read_csv("data/processed/final_data.csv")
print(f"Dataset: {len(df):,} rows")

TARGET = 'delay_ratio'

# ── Feature sets ──────────────────────────────────────────────────────
BASELINE_FEATURES = [
    'segment_osrm_distance',
    'segment_osrm_time',
    'osrm_speed_kmpm',
    'hour',
    'day_of_week',
    'is_weekend',
    'is_peak',
    'is_ftl',
    'is_cutoff',
    'cutoff_factor',
]

GRAPH_FEATURES = BASELINE_FEATURES + [
    'source_betweenness',
    'source_pagerank',
    'source_indegree',
    'source_outdegree',
    'source_clustering',
    'dest_betweenness',
    'dest_pagerank',
]

# Only keep rows where all features are present
df_model = df[GRAPH_FEATURES + [TARGET]].dropna()
print(f"Rows after dropping NaN: {len(df_model):,}")

X_baseline = df_model[BASELINE_FEATURES]
X_graph    = df_model[GRAPH_FEATURES]
y          = df_model[TARGET]

X_b_train, X_b_test, y_train, y_test = train_test_split(
    X_baseline, y, test_size=0.2, random_state=42)
X_g_train = X_graph.iloc[X_b_train.index - X_b_train.index.min()]
X_g_test  = X_graph.iloc[X_b_test.index  - X_b_test.index.min()]

# Re-split properly
idx_train, idx_test = train_test_split(df_model.index, test_size=0.2, random_state=42)
X_b_train = df_model.loc[idx_train, BASELINE_FEATURES]
X_b_test  = df_model.loc[idx_test,  BASELINE_FEATURES]
X_g_train = df_model.loc[idx_train, GRAPH_FEATURES]
X_g_test  = df_model.loc[idx_test,  GRAPH_FEATURES]
y_train   = df_model.loc[idx_train, TARGET]
y_test    = df_model.loc[idx_test,  TARGET]

XGB_PARAMS = dict(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=7,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)

# ── Train Baseline ────────────────────────────────────────────────────
print("\nTraining Baseline model (no graph features)...")
baseline_model = XGBRegressor(**XGB_PARAMS)
baseline_model.fit(X_b_train, y_train,
                   eval_set=[(X_b_test, y_test)],
                   verbose=False)
baseline_preds = baseline_model.predict(X_b_test)

# ── Train Graph-Enhanced ──────────────────────────────────────────────
print("Training Graph-Enhanced model...")
graph_model = XGBRegressor(**XGB_PARAMS)
graph_model.fit(X_g_train, y_train,
                eval_set=[(X_g_test, y_test)],
                verbose=False)
graph_preds = graph_model.predict(X_g_test)

# ── Evaluation ────────────────────────────────────────────────────────
def within_pct(actual, pred, pct=0.15):
    return np.mean(np.abs(pred - actual) / (actual + 1e-6) <= pct) * 100

b_mae   = mean_absolute_error(y_test, baseline_preds)
g_mae   = mean_absolute_error(y_test, graph_preds)
b_acc   = within_pct(y_test.values, baseline_preds)
g_acc   = within_pct(y_test.values, graph_preds)
impr    = (b_mae - g_mae) / b_mae * 100

print("\n" + "="*55)
print("MODEL BENCHMARKING RESULTS")
print("="*55)
print(f"{'Metric':<30} {'Baseline':>10} {'Graph-Enhanced':>15}")
print("-"*55)
print(f"{'MAE (delay ratio)':<30} {b_mae:>10.4f} {g_mae:>15.4f}")
print(f"{'Within-15% accuracy (%)':<30} {b_acc:>10.1f} {g_acc:>15.1f}")
print(f"{'MAE Improvement (%)':<30} {'—':>10} {impr:>14.1f}%")
print("="*55)

if impr >= 15:
    print(f"\n✅ Graph advantage confirmed: {impr:.1f}% MAE improvement (target: 15%)")
else:
    print(f"\n⚠️  Graph improvement: {impr:.1f}% — below 15% target. "
          f"Consider tuning or adding node2vec embeddings.")

# ── Feature importance ────────────────────────────────────────────────
feat_imp = pd.DataFrame({
    'feature': GRAPH_FEATURES,
    'importance': graph_model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nTop 10 Features (Graph Model):")
print(feat_imp.head(10).to_string(index=False))

# ── Save ──────────────────────────────────────────────────────────────
os.makedirs("models", exist_ok=True)
joblib.dump(baseline_model, "models/baseline_xgb.pkl")
joblib.dump(graph_model,    "models/graph_xgb.pkl")

results = {
    "baseline_mae":   round(b_mae, 4),
    "graph_mae":      round(g_mae, 4),
    "baseline_acc15": round(b_acc, 2),
    "graph_acc15":    round(g_acc, 2),
    "mae_improvement_pct": round(impr, 2),
    "n_test_samples": int(len(y_test))
}
with open("models/benchmark_results.json", "w") as f:
    json.dump(results, f, indent=2)
feat_imp.to_csv("models/feature_importance.csv", index=False)
print("\n✅ Models and results saved.")
