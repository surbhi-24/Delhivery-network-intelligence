"""
ftl_carting_framework.py
Delhivery Network Intelligence — ML-Backed FTL vs Carting Decision Framework

Unlike a descriptive comparison, this builds an actual decision framework:
given a corridor's profile, what route type minimises predicted delay?
We also quantify the time-cost tradeoff for operations teams.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os

df = pd.read_csv("data/processed/final_data.csv")
os.makedirs("visualizations/output", exist_ok=True)

# ── 1. Statistical comparison ─────────────────────────────────────────
ftl     = df[df['route_type'] == 'FTL']['delay_ratio']
carting = df[df['route_type'] == 'Carting']['delay_ratio']

stats = pd.DataFrame({
    'Route Type':  ['FTL', 'Carting'],
    'Count':       [len(ftl), len(carting)],
    'Mean Delay':  [ftl.mean(), carting.mean()],
    'Median Delay':[ftl.median(), carting.median()],
    'Std Dev':     [ftl.std(), carting.std()],
    'SLA Breach%': [
        df[df['route_type']=='FTL']['sla_breach'].mean()*100,
        df[df['route_type']=='Carting']['sla_breach'].mean()*100
    ],
    'Severe Delay%':[
        df[df['route_type']=='FTL']['severe_delay'].mean()*100,
        df[df['route_type']=='Carting']['severe_delay'].mean()*100
    ]
})
stats = stats.round(3)
stats.to_csv("visualizations/ftl_carting_stats.csv", index=False)
print(stats.to_string(index=False))

# ── 2. Decision rule derivation ───────────────────────────────────────
# For each distance bucket, compare FTL vs Carting median delay
corridor_comparison = (
    df.groupby(['dist_bucket', 'route_type'])['delay_ratio']
    .agg(['median', 'mean', 'count'])
    .reset_index()
)
corridor_comparison.to_csv("visualizations/corridor_route_comparison.csv", index=False)

# ── 3. Betweenness × Route type analysis ─────────────────────────────
# Key insight: does graph position (centrality) affect whether FTL or 
# Carting performs better? This is the "graph advantage" for operations.
df['centrality_bin'] = pd.qcut(df['source_betweenness'], 
                                q=4, 
                                labels=['Low','Medium','High','Critical'])
pivot_route_cent = (
    df.groupby(['centrality_bin', 'route_type'])['delay_ratio']
    .median()
    .unstack()
    .round(3)
)
print("\nMedian delay by hub centrality & route type:")
print(pivot_route_cent)

# ── 4. FTL conversion priority list ──────────────────────────────────
# Corridors that are currently Carting, high delay, and good FTL candidates
carting_corridors = (
    df[df['route_type'] == 'Carting']
    .groupby(['source_name', 'destination_name'])
    .agg(
        avg_delay = ('delay_ratio', 'median'),
        trip_count = ('trip_uuid', 'count'),
        sla_breach_rate = ('sla_breach', 'mean'),
        source_betweenness = ('source_betweenness', 'first')
    )
    .reset_index()
)
carting_corridors = carting_corridors[carting_corridors['trip_count'] >= 10]

# Score = delay × sla_breach_rate × (1 + betweenness) — conversion priority
carting_corridors['conversion_priority_score'] = (
    carting_corridors['avg_delay'] * 
    carting_corridors['sla_breach_rate'] * 
    (1 + carting_corridors['source_betweenness'] * 100)
)
top_convert = carting_corridors.nlargest(15, 'conversion_priority_score')
top_convert.to_csv("visualizations/ftl_conversion_candidates.csv", index=False)
print(f"\nTop 15 Carting→FTL conversion candidates saved.")

# ── 5. Visualisations ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("FTL vs Carting — Delay Analysis", fontsize=14, fontweight='bold')

# Violin plot
ax = axes[0]
data_plot = df[df['delay_ratio'] <= df['delay_ratio'].quantile(0.95)]
parts = ax.violinplot(
    [data_plot[data_plot['route_type']=='FTL']['delay_ratio'].dropna(),
     data_plot[data_plot['route_type']=='Carting']['delay_ratio'].dropna()],
    positions=[1, 2], showmedians=True
)
for pc in parts['bodies']:
    pc.set_alpha(0.7)
ax.set_xticks([1, 2])
ax.set_xticklabels(['FTL', 'Carting'])
ax.set_ylabel('Delay Ratio (actual / OSRM)')
ax.set_title('Delay Distribution by Route Type')
ax.axhline(1.0, color='red', linestyle='--', alpha=0.5, label='On-time baseline')
ax.legend()

# SLA breach by distance bucket
ax2 = axes[1]
pivot = (df.groupby(['dist_bucket', 'route_type'])['sla_breach']
           .mean()
           .unstack() * 100)
pivot.plot(kind='bar', ax=ax2, color=['#2563eb', '#f59e0b'], edgecolor='white')
ax2.set_title('SLA Breach Rate by Distance & Route Type')
ax2.set_ylabel('SLA Breach Rate (%)')
ax2.set_xlabel('Distance Bucket')
ax2.tick_params(axis='x', rotation=30)
ax2.legend(title='Route Type')

plt.tight_layout()
plt.savefig("visualizations/output/ftl_carting_analysis.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ FTL vs Carting analysis saved.")
