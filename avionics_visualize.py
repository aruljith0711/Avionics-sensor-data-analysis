"""
============================================================
Avionics Sensor Data Analysis & Anomaly Detection
Script  : avionics_visualize.py
Purpose : Generate 4 publication-quality plots:
          1. Time-series with anomaly highlights (6 panels)
          2. Sensor correlation heatmap
          3. Anomaly count bar chart per channel
          4. Subsystem health KPI dashboard
Author  : P B Aruljith
============================================================
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── CONFIGURATION ─────────────────────────────────────────────
DATA_PATH   = 'D:/AnalyticsProjects/Flight Data/avionics_export.csv'
OUTPUT_DIR  = 'D:/AnalyticsProjects/Flight Data/outputs/'

PARAMS      = ['Altitude', 'Airspeed', 'Pitch', 'Roll', 'EngineN1', 'Temperature']
Z_THRESHOLD = 3

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── LOAD & PREPARE ────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df = df.ffill()
df.drop_duplicates(inplace=True)

# Recompute anomaly flags
z_scores    = pd.DataFrame(
    np.abs(stats.zscore(df[PARAMS].fillna(0))),
    columns=PARAMS
)
z_anomalies = (z_scores > Z_THRESHOLD)

# Use DataFrame index as time axis (sample number)
time_axis   = df.index

print("Generating plots...")

# ── PLOT 1: TIME-SERIES WITH ANOMALIES ───────────────────────
fig, axes = plt.subplots(3, 2, figsize=(16, 12))
axes = axes.flatten()

for i, col in enumerate(PARAMS):
    # Main sensor line
    axes[i].plot(
        time_axis, df[col],
        color='steelblue', linewidth=0.7, alpha=0.85, label=col
    )
    # Anomaly overlay — red dots on top
    anomaly_idx    = df[z_anomalies[col]]
    axes[i].scatter(
        anomaly_idx.index, anomaly_idx[col],
        color='red', s=15, zorder=5, label='Anomaly'
    )
    anomaly_count = z_anomalies[col].sum()
    axes[i].set_title(f'{col}  ({anomaly_count} anomalies)', fontsize=11)
    axes[i].set_xlabel('Sample Number', fontsize=9)
    axes[i].set_ylabel(col, fontsize=9)
    axes[i].legend(fontsize=8)
    axes[i].grid(True, alpha=0.3)

plt.suptitle(
    'Avionics Sensor Time-Series — Anomaly Detection (Z-score)',
    fontsize=14, fontweight='bold', y=1.01
)
plt.tight_layout()
path1 = os.path.join(OUTPUT_DIR, 'timeseries_anomalies.png')
plt.savefig(path1, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {path1}")

# ── PLOT 2: CORRELATION HEATMAP ───────────────────────────────
corr_matrix = df[PARAMS].corr()

plt.figure(figsize=(9, 7))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt='.2f',
    cmap='coolwarm',
    linewidths=0.5,
    square=True,
    vmin=-1, vmax=1,
    annot_kws={'size': 11}
)
plt.title('Sensor Parameter Correlation Heatmap\n(Pearson Correlation Coefficients)',
          fontsize=13, fontweight='bold')
plt.tight_layout()
path2 = os.path.join(OUTPUT_DIR, 'correlation_heatmap.png')
plt.savefig(path2, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {path2}")

# ── PLOT 3: ANOMALY COUNT BAR CHART ──────────────────────────
anomaly_counts = z_anomalies.sum()

plt.figure(figsize=(10, 5))
bars = plt.bar(
    PARAMS, anomaly_counts,
    color='tomato', edgecolor='darkred', linewidth=0.8
)
# Add value labels on top of each bar
for bar, val in zip(bars, anomaly_counts):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(anomaly_counts) * 0.01,
        str(val), ha='center', va='bottom', fontsize=10, fontweight='bold'
    )
plt.title('Anomaly Count per Sensor Channel (Z-score Method)',
          fontsize=13, fontweight='bold')
plt.ylabel('Number of Anomalous Readings', fontsize=11)
plt.xlabel('Sensor Channel', fontsize=11)
plt.xticks(rotation=20, ha='right')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
path3 = os.path.join(OUTPUT_DIR, 'anomaly_distribution.png')
plt.savefig(path3, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {path3}")

# ── PLOT 4: SUBSYSTEM HEALTH KPI DASHBOARD ───────────────────
health_score = 100 - (z_anomalies.sum() / len(df) * 100)
colors = [
    'green'  if v > 95 else
    'orange' if v > 90 else
    'red'
    for v in health_score
]

plt.figure(figsize=(10, 6))
bars = plt.bar(PARAMS, health_score, color=colors, edgecolor='black', linewidth=0.7)

# Value labels
for bar, val in zip(bars, health_score):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() - 1.5,
        f'{val:.1f}%', ha='center', va='top',
        fontsize=10, fontweight='bold', color='white'
    )

plt.axhline(y=95, color='green',  linestyle='--', linewidth=1.2,
            label='Healthy threshold  (>95%)')
plt.axhline(y=90, color='orange', linestyle='--', linewidth=1.2,
            label='Warning threshold  (>90%)')

plt.title('Subsystem Health KPI — % Normal Readings per Channel',
          fontsize=13, fontweight='bold')
plt.ylabel('Health Score (%)', fontsize=11)
plt.xlabel('Sensor Channel', fontsize=11)
plt.ylim(75, 102)
plt.xticks(rotation=20, ha='right')
plt.legend(fontsize=10)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
path4 = os.path.join(OUTPUT_DIR, 'health_kpi_dashboard.png')
plt.savefig(path4, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {path4}")

print("\nAll 4 plots saved successfully.")
