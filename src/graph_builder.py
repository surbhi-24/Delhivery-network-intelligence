"""
graph_builder.py
Delhivery Network Intelligence — Graph Construction & Centrality Analysis

Approach: Build a directed weighted graph where each edge (u→v) represents
a corridor. Edge weight = median delay_ratio (not mean — more robust to 
the long tail we saw in EDA). We compute 4 structural metrics per node
to use as ML features.
"""

import pandas as pd
import numpy as np
import networkx as nx
import json
import os

df = pd.read_csv("data/processed/cleaned_data.csv")
print(f"Building graph from {len(df):,} trips...")

# ── Build directed graph ──────────────────────────────────────────────
# Use MEDIAN delay per corridor (robust to outliers; friend used mean which
# gets pulled by extreme values)
corridor_stats = (df.groupby(['source_center', 'destination_center'])
                    .agg(
                        median_delay = ('delay_ratio', 'median'),
                        mean_delay   = ('delay_ratio', 'mean'),
                        trip_count   = ('trip_uuid', 'count'),
                        sla_breach_rate = ('sla_breach', 'mean')
                    )
                    .reset_index())

G = nx.DiGraph()
for _, row in corridor_stats.iterrows():
    G.add_edge(
        row['source_center'],
        row['destination_center'],
        weight        = row['median_delay'],
        mean_delay    = row['mean_delay'],
        trip_count    = row['trip_count'],
        sla_breach_rt = row['sla_breach_rate']
    )

print(f"Graph: {G.number_of_nodes()} nodes (facilities), "
      f"{G.number_of_edges()} edges (corridors)")

# ── Structural metrics ────────────────────────────────────────────────
print("Computing betweenness centrality (may take ~30s)...")
betweenness  = nx.betweenness_centrality(G, weight='weight', normalized=True)

print("Computing PageRank...")
pagerank     = nx.pagerank(G, weight='weight')

in_degree    = dict(G.in_degree(weight='weight'))
out_degree   = dict(G.out_degree(weight='weight'))
degree       = dict(G.degree())

# Clustering on undirected version
G_undirected = G.to_undirected()
clustering   = nx.clustering(G_undirected)

# ── Attach to dataframe ───────────────────────────────────────────────
df['source_betweenness'] = df['source_center'].map(betweenness).fillna(0)
df['source_pagerank']    = df['source_center'].map(pagerank).fillna(0)
df['source_indegree']    = df['source_center'].map(in_degree).fillna(0)
df['source_outdegree']   = df['source_center'].map(out_degree).fillna(0)
df['source_clustering']  = df['source_center'].map(clustering).fillna(0)
df['dest_betweenness']   = df['destination_center'].map(betweenness).fillna(0)
df['dest_pagerank']      = df['destination_center'].map(pagerank).fillna(0)

df.to_csv("data/processed/final_data.csv", index=False)
print("Saved: data/processed/final_data.csv")

# ── Top bottleneck hubs ───────────────────────────────────────────────
top5 = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]

# Enrich with hub names (source_name)
hub_name_map = df.drop_duplicates('source_center').set_index('source_center')['source_name'].to_dict()

top5_enriched = []
for rank_idx, (center_id, score) in enumerate(top5, start=1):
    hub_name = hub_name_map.get(center_id, center_id)
    sla = corridor_stats[corridor_stats['source_center'] == center_id]['sla_breach_rate'].mean()
    sla_val = float(sla) if not pd.isna(sla) else 0
    # Composite priority score: betweenness × sla_breach_rate × 100
    composite = round(score * sla_val * 100, 2)
    top5_enriched.append({
        "rank": rank_idx,
        "center_id": center_id,
        "hub_name":  hub_name,
        "betweenness": round(score, 5),
        "avg_sla_breach_rate": round(sla_val, 3),
        "composite_score": composite
    })

os.makedirs("visualizations", exist_ok=True)
with open("visualizations/top5_hubs.json", "w") as f:
    json.dump(top5_enriched, f, indent=2)

print("\n🔴 Top 5 Bottleneck Hubs (by Betweenness Centrality):")
for h in top5_enriched:
    print(f"  {h['hub_name'][:40]:<40} | centrality={h['betweenness']:.5f} | "
          f"SLA breach={h['avg_sla_breach_rate']*100:.1f}%")
