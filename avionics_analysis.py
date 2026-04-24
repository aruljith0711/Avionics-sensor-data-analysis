"""
============================================================
Avionics Sensor Data Analysis & Anomaly Detection
Script  : avionics_analysis.py
Purpose : Load exported CSV, clean data, apply Z-score and
          IQR anomaly detection across 6 sensor channels,
          and print a full statistical summary.
Author  : P B Aruljith
============================================================
"""

import pandas as pd
import numpy as np
from scipy import stats

# ── CONFIGURATION ─────────────────────────────────────────────
DATA_PATH = 'D:/AnalyticsProjects/Flight Data/avionics_export.csv'

PARAMS = ['Altitude', 'Airspeed', 'Pitch', 'Roll', 'EngineN1', 'Temperature']

Z_THRESHOLD  = 3      # Standard deviations for Z-score flagging
IQR_FENCE    = 1.5    # Tukey's fence multiplier for IQR

# ── STEP 1: LOAD DATA ─────────────────────────────────────────
print("=" * 55)
print("AVIONICS SENSOR DATA ANALYSIS")
print("=" * 55)

df = pd.read_csv(DATA_PATH)

print(f"\nShape           : {df.shape}")
print(f"Columns         : {df.columns.tolist()}")
print(f"\n--- Basic Statistics ---")
print(df[PARAMS].describe().round(4))

# ── STEP 2: DATA CLEANING ─────────────────────────────────────
print(f"\n--- Missing Values (before cleaning) ---")
print(df.isnull().sum())

# Forward fill — propagates last valid reading (suitable for time-series)
df = df.ffill()

# Remove exact duplicate rows
df.drop_duplicates(inplace=True)

print(f"\nMissing values after cleaning : {df.isnull().sum().sum()}")
print(f"Shape after cleaning          : {df.shape}")

# ── STEP 3: Z-SCORE ANOMALY DETECTION ────────────────────────
# Compute absolute Z-scores for all sensor columns simultaneously
z_scores   = pd.DataFrame(
    np.abs(stats.zscore(df[PARAMS].fillna(0))),
    columns=PARAMS
)
z_anomalies = (z_scores > Z_THRESHOLD)

print(f"\n--- Anomalies Detected (Z-score, threshold={Z_THRESHOLD}) ---")
print(z_anomalies.sum())

# ── STEP 4: IQR ANOMALY DETECTION ────────────────────────────
iqr_anomalies = pd.DataFrame(False, index=df.index, columns=PARAMS)

for col in PARAMS:
    Q1    = df[col].quantile(0.25)
    Q3    = df[col].quantile(0.75)
    IQR   = Q3 - Q1
    lower = Q1 - IQR_FENCE * IQR
    upper = Q3 + IQR_FENCE * IQR
    iqr_anomalies[col] = (df[col] < lower) | (df[col] > upper)

print(f"\n--- Anomalies Detected (IQR, fence={IQR_FENCE}) ---")
print(iqr_anomalies.sum())

# ── STEP 5: COMBINED FLAG ─────────────────────────────────────
# Union approach — flag if either method detects anomaly
combined_flag = z_anomalies | iqr_anomalies

print(f"\n--- Combined Anomaly Flags (Z-score OR IQR) ---")
print(combined_flag.sum())

# ── STEP 6: CORRELATION ANALYSIS ─────────────────────────────
corr_matrix = df[PARAMS].corr()

print(f"\n--- Pearson Correlation Matrix ---")
print(corr_matrix.round(4))

# ── STEP 7: HEALTH SCORE SUMMARY ─────────────────────────────
health_score = 100 - (z_anomalies.sum() / len(df) * 100)

print(f"\n--- Subsystem Health Score (% Normal Readings) ---")
for col in PARAMS:
    status = "HEALTHY" if health_score[col] > 95 else \
             "WARNING" if health_score[col] > 90 else "CRITICAL"
    print(f"  {col:<15}: {health_score[col]:.2f}%  [{status}]")

print(f"\nAnalysis complete. Run avionics_visualize.py for plots.")

# ── EXPORT PROCESSED DATA ─────────────────────────────────────
df.to_csv('D:/AnalyticsProjects/Flight Data/avionics_processed.csv', index=False)
print("Processed data saved to avionics_processed.csv")
