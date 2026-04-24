"""
============================================================
Avionics Sensor Data Analysis & Anomaly Detection
Script  : cross_validation.py
Purpose : Compare correlation matrices computed independently
          in Octave and Python to validate pipeline consistency.
          Max difference near 0 confirms both environments
          processed the data identically.
Author  : P B Aruljith
============================================================
"""

import pandas as pd
import numpy as np

# ── CONFIGURATION ─────────────────────────────────────────────
DATA_PATH       = 'D:/AnalyticsProjects/Flight Data/avionics_export.csv'
MATLAB_CORR     = 'D:/AnalyticsProjects/Flight Data/matlab_corr.csv'

PARAMS          = ['Altitude', 'Airspeed', 'Pitch', 'Roll', 'EngineN1', 'Temperature']
PASS_THRESHOLD  = 0.01   # Max acceptable difference between matrices

# ── LOAD DATA ─────────────────────────────────────────────────
df            = pd.read_csv(DATA_PATH)
df_matlab     = pd.read_csv(MATLAB_CORR, header=None)

# ── COMPUTE PYTHON CORRELATION ────────────────────────────────
python_corr   = df[PARAMS].corr().values

# ── LOAD MATLAB CORRELATION ───────────────────────────────────
matlab_corr   = df_matlab.values

print("=" * 55)
print("CROSS-VALIDATION: OCTAVE vs PYTHON")
print("=" * 55)

# ── PYTHON CORRELATION ────────────────────────────────────────
print("\nPython Correlation Matrix:")
print(pd.DataFrame(python_corr, columns=PARAMS, index=PARAMS).round(4).to_string())

# ── MATLAB CORRELATION ────────────────────────────────────────
print("\nOctave Correlation Matrix:")
print(pd.DataFrame(matlab_corr, columns=PARAMS, index=PARAMS).round(4).to_string())

# ── DIFFERENCE MATRIX ─────────────────────────────────────────
diff = np.abs(python_corr - matlab_corr)

print("\nAbsolute Difference Matrix:")
print(pd.DataFrame(diff, columns=PARAMS, index=PARAMS).round(6).to_string())

# ── VALIDATION RESULT ─────────────────────────────────────────
max_diff  = np.max(diff)
mean_diff = np.mean(diff)

print(f"\nMax difference  : {max_diff:.6f}")
print(f"Mean difference : {mean_diff:.6f}")
print(f"Pass threshold  : {PASS_THRESHOLD}")

if max_diff < PASS_THRESHOLD:
    print("\nValidation PASSED — Octave and Python results are consistent.")
else:
    print("\nValidation WARNING — Differences detected. Check NaN handling.")
    # Find which pairs differ most
    diff_df = pd.DataFrame(diff, columns=PARAMS, index=PARAMS)
    max_pair = np.unravel_index(diff.argmax(), diff.shape)
    print(f"  Largest mismatch: {PARAMS[max_pair[0]]} vs {PARAMS[max_pair[1]]}  ({diff[max_pair]:.6f})")
