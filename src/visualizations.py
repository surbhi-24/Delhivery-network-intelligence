"""
visualizations.py
Delhivery Network Intelligence — Network Graph & Heatmaps

Three outputs:
  1. Network graph (top 80 nodes) with centrality coloring
  2. Corridor delay heatmap (top 20 source × destination)
  3. Hourly delay pattern (actionable for dispatch scheduling)
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import json
import os

os.makedirs("visualizations/output", exist_ok=True)
df = pd.read_csv("data/processed/final_data.csv")

# ── Load centrality already computed ────────────────────────────────
with open("visualizations/top5_hubs.json") as f:
    top5 = json.load(f)

# ── 1. Network graph ─────────────────────────────────────────────────
print("Building network graph...")
G = nx.DiGraph()
corridor_stats = (df.groupby(['source_center', 'destination_center'])
                    .agg(median_delay=('delay_ratio', 'median'),
                         trip_count=('trip_uuid', 'count'))
                    .reset_index())

for _, r in corridor_stats.iterrows():
    G.add_edge(r['source_center'], r['destination_center'],
               weight=r['median_delay'])

betweenness = nx.betweenness_centrality(G, weight='weight', normalized=True)

# Subgraph: top 80 hubs
top_nodes = sorted(betweenness, key=betweenness.get, reverse=True)[:80]
H = G.subgraph(top_nodes)
node_list = list(H.nodes())
cent_vals  = [betweenness.get(n, 0) for n in node_list]

import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

BG        = '#0d1117'    # near-black background
EDGE_BASE = '#3a4a6b'    # dim blue-grey for normal edges
HIGH_EDGE = '#ff6b6b'    # reddish for high-delay corridors

fig, ax = plt.subplots(figsize=(22, 15))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

cmap  = plt.cm.RdYlGn_r
norm  = mcolors.Normalize(vmin=min(cent_vals), vmax=max(cent_vals))
colors = [cmap(norm(v)) for v in cent_vals]

node_sizes = [250 + 2800 * betweenness.get(n, 0) / max(cent_vals) for n in node_list]

pos = nx.spring_layout(H, seed=42, k=2.5, iterations=60)

# Layer 1 — all edges, thin & dim, slight curve so overlapping arrows are visible
nx.draw_networkx_edges(H, pos, alpha=0.35, arrows=True,
                        arrowstyle='->', arrowsize=10,
                        edge_color=EDGE_BASE, width=0.7, ax=ax,
                        connectionstyle='arc3,rad=0.05')

# Layer 2 — high-delay corridors (delay_ratio > 1.5), highlighted in red
high_delay = [(u, v) for u, v, d in H.edges(data=True) if d.get('weight', 0) > 1.5]
if high_delay:
    nx.draw_networkx_edges(H, pos, edgelist=high_delay,
                            alpha=0.65, arrows=True,
                            arrowstyle='->', arrowsize=14,
                            edge_color=HIGH_EDGE, width=1.6, ax=ax,
                            connectionstyle='arc3,rad=0.05')

nx.draw_networkx_nodes(H, pos, nodelist=node_list,
                        node_color=colors, node_size=node_sizes,
                        alpha=0.95, linewidths=1.0,
                        edgecolors='white', ax=ax)

# Labels
top5_ids = [h["center_id"] for h in top5]
name_map = df.drop_duplicates('source_center').set_index('source_center')['source_name'].to_dict()

all_labels = {n: name_map.get(n, n)[:13] for n in node_list}
nx.draw_networkx_labels(H, pos, labels=all_labels,
                         font_size=5, font_color='#cccccc', ax=ax)

top_labels = {n: name_map.get(n, n)[:22] for n in top5_ids if n in node_list}
label_handles = nx.draw_networkx_labels(H, pos, labels=top_labels,
                                         font_size=8, font_color='white',
                                         font_weight='bold', ax=ax)
for _, t in label_handles.items():
    t.set_path_effects([pe.withStroke(linewidth=3, foreground='black')])

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, fraction=0.022, pad=0.02, shrink=0.8)
cbar.set_label('Betweenness Centrality (Bottleneck Score)', color='white', fontsize=11)
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')
cbar.outline.set_edgecolor('white')

legend_elements = [
    Line2D([0],[0], color=EDGE_BASE, lw=1.5, label='Corridor (normal delay)'),
    Line2D([0],[0], color=HIGH_EDGE, lw=2.5, label='Corridor (delay ratio > 1.5×)'),
]
ax.legend(handles=legend_elements, loc='lower left',
          facecolor='#1c2333', edgecolor='white',
          labelcolor='white', fontsize=9, framealpha=0.8)

ax.set_title("Delhivery Logistics Network — Bottleneck Hub Analysis\n"
             "(Red = High Risk  |  Green = Low Risk  |  Node size ∝ Centrality)",
             fontsize=14, fontweight='bold', color='white', pad=20)
ax.axis('off')
plt.tight_layout()
plt.savefig("visualizations/output/network_graph.png",
            dpi=160, bbox_inches='tight', facecolor=BG)
plt.close()
print("✅ Network graph saved.")

# ── 2. Corridor delay heatmap ────────────────────────────────────────
pivot = df.pivot_table(index='source_name', columns='destination_name',
                        values='delay_ratio', aggfunc='median')
top_src = df.groupby('source_name')['delay_ratio'].median().nlargest(18).index
top_dst = df.groupby('destination_name')['delay_ratio'].median().nlargest(18).index
pivot = pivot.loc[pivot.index.isin(top_src), pivot.columns.isin(top_dst)]

fig, ax = plt.subplots(figsize=(16, 11))
sns.heatmap(pivot, cmap='YlOrRd', linewidths=0.15,
            cbar_kws={'label': 'Median Delay Ratio (actual/OSRM)'},
            annot=False, ax=ax)
ax.set_title("Corridor Delay Heatmap: Source → Destination\n"
             "(Top 18 highest-delay hubs — median delay ratio)",
             fontsize=13, fontweight='bold')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=7)
plt.tight_layout()
plt.savefig("visualizations/output/heatmap_corridor.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Corridor heatmap saved.")

# ── 3. 24-hour delay pattern ─────────────────────────────────────────
hourly = df.groupby('hour')['delay_ratio'].agg(['mean', 'median', 'std']).reset_index()

fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(hourly['hour'], hourly['mean'] - hourly['std']/2,
                hourly['mean'] + hourly['std']/2, alpha=0.2, color='#6366f1')
ax.plot(hourly['hour'], hourly['mean'],   color='#6366f1', lw=2.5, label='Mean delay')
ax.plot(hourly['hour'], hourly['median'], color='#f59e0b', lw=2,
        linestyle='--', label='Median delay')
ax.axhline(1.0, color='#ef4444', linestyle=':', lw=1.5, label='OSRM baseline (1.0×)')
ax.set_xlabel("Hour of Day", fontsize=11)
ax.set_ylabel("Delay Ratio", fontsize=11)
ax.set_title("24-Hour Delay Pattern — Mean & Median Delay Ratio\n"
             "(Shaded band = ±½ std; use this for dispatch window planning)",
             fontsize=12, fontweight='bold')
ax.set_xticks(range(0, 24, 2))
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("visualizations/output/hourly_delay_pattern.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Hourly pattern saved.")

# ── 4. Cutoff-impact heatmap ─────────────────────────────────────────
if 'is_cutoff' in df.columns:
    df['is_cutoff'] = df['is_cutoff'].astype(str)

    pivot_cutoff = df.pivot_table(
        index='source_name',
        columns='is_cutoff',
        values='delay_ratio',
        aggfunc='mean'
    ).fillna(0)

    top_cutoff = df.groupby('source_name')['delay_ratio'] \
                   .mean().nlargest(25).index

    pivot_cutoff = pivot_cutoff.loc[
        pivot_cutoff.index.isin(top_cutoff)
    ]

    fig, ax = plt.subplots(figsize=(9, 12))

    sns.heatmap(
        pivot_cutoff,
        cmap='PuRd',
        annot=True,
        fmt='.2f',
        linewidths=0.3,
        cbar_kws={'label': 'Avg Delay Factor'},
        ax=ax
    )

    ax.set_title(
        'Delay Factor: Cutoff vs Non-Cutoff Shipments by Hub',
        fontsize=13,
        fontweight='bold'
    )

    ax.set_xlabel('Is Cutoff')
    ax.set_ylabel('Source Hub')

    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=7)

    plt.tight_layout()

    plt.savefig(
        'visualizations/output/heatmap_cutoff.png',
        dpi=150,
        bbox_inches='tight'
    )

    plt.close()

    print('✅ Cutoff heatmap saved.')

# ── 5. Route-type delay heatmap ──────────────────────────────────────
# FTL vs Carting delay by time window AND centrality bin
# Distinct from FTL analysis chart — this is a 2D heatmap grid
if 'route_type' in df.columns and 'source_betweenness' in df.columns:
    df['centrality_bin'] = pd.qcut(
        df['source_betweenness'],
        q=4,
        labels=['Low (Q1)', 'Medium (Q2)', 'High (Q3)', 'Critical (Q4)']
    )
    pivot_rt = df.pivot_table(
        index='centrality_bin',
        columns='route_type',
        values='delay_ratio',
        aggfunc='median'
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot_rt, cmap='RdYlGn_r', annot=True, fmt='.3f',
                linewidths=0.4, ax=ax,
                cbar_kws={'label': 'Median Delay Ratio (actual/OSRM)'},
                vmin=1.5, vmax=2.5)
    ax.set_title('Route Type × Hub Centrality: Median Delay\n'
                 '(Does FTL advantage hold at critical hubs?)',
                 fontsize=11, fontweight='bold')
    ax.set_xlabel('Route Type')
    ax.set_ylabel('Source Hub Centrality Quartile')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    plt.tight_layout()
    plt.savefig('visualizations/output/heatmap_routetype.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('✅ Route-type heatmap saved.')
