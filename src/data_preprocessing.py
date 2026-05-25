"""
data_preprocessing.py
Delhivery Network Intelligence — Data Pipeline

Key design choice: we use segment_factor (actual_time / osrm_time) as the
delay metric, NOT the raw difference. This is dimensionless and comparable
across corridors of different lengths — a better target for the ML model.
"""

import pandas as pd
import numpy as np
import os

# ── Load ──────────────────────────────────────────────────────────────
df = pd.read_csv("delivery_data.csv")
print(f"Raw dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ── Deduplication ─────────────────────────────────────────────────────
before = len(df)
df.drop_duplicates(subset='trip_uuid', inplace=True)
print(f"Dropped {before - len(df)} duplicate trip_uuids")

# ── Drop rows with missing key columns ───────────────────────────────
df.dropna(subset=['source_name', 'destination_name',
                  'segment_factor', 'actual_time', 'osrm_time'], inplace=True)

# ── Remove physically impossible values ──────────────────────────────
# Negative segment_factor means data error; cap extreme outliers
df = df[df['segment_factor'] > 0]
df = df[df['actual_time'] > 0]
df = df[df['osrm_time'] > 0]

# Winsorize segment_factor at 99th percentile (outliers like 574x are noise)
cap = df['segment_factor'].quantile(0.99)
df['segment_factor_raw'] = df['segment_factor']
df['segment_factor'] = df['segment_factor'].clip(upper=cap)
print(f"Winsorized segment_factor cap at 99th pct: {cap:.2f}x")

# ── Target variable ───────────────────────────────────────────────────
# delay_ratio = segment_factor (already actual/osrm per segment)
df['delay_ratio'] = df['segment_factor']

# Secondary targets
df['sla_breach'] = (df['delay_ratio'] > 1.2).astype(int)  # >20% over OSRM
df['severe_delay'] = (df['delay_ratio'] > 2.0).astype(int)

# ── Time features ─────────────────────────────────────────────────────
df['trip_creation_time'] = pd.to_datetime(df['trip_creation_time'], errors='coerce')
df['od_start_time'] = pd.to_datetime(df['od_start_time'], errors='coerce')

df['hour']       = df['od_start_time'].dt.hour
df['day_of_week'] = df['od_start_time'].dt.dayofweek   # 0=Monday
df['month']      = df['od_start_time'].dt.month
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

# Morning rush, evening rush, night
df['time_window'] = pd.cut(df['hour'],
                           bins=[-1, 6, 10, 14, 18, 22, 24],
                           labels=['night','morning_rush','afternoon',
                                   'evening_rush','late_evening','midnight'])

df['is_peak'] = df['hour'].between(8, 11).astype(int)

# ── Route features ────────────────────────────────────────────────────
df['is_ftl'] = (df['route_type'] == 'FTL').astype(int)

# Distance bucket
df['dist_bucket'] = pd.cut(df['segment_osrm_distance'],
                            bins=[0, 50, 150, 300, 1e6],
                            labels=['short','medium','long','very_long'])

# Speed proxy: osrm_distance / osrm_time (km per minute)
df['osrm_speed_kmpm'] = df['segment_osrm_distance'] / (df['segment_osrm_time'] + 1e-6)

os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/cleaned_data.csv", index=False)
print(f"\nCleaned dataset saved: {df.shape[0]:,} rows")
print(f"SLA breach rate: {df['sla_breach'].mean()*100:.1f}%")
print(f"Severe delay rate: {df['severe_delay'].mean()*100:.1f}%")
print(f"FTL vs Carting: {df['route_type'].value_counts().to_dict()}")
