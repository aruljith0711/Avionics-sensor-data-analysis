# Avionics Sensor Data Analysis

An end-to-end data analytics pipeline for avionics sensor telemetry — covering multi-source data ingestion, cleaning, statistical anomaly detection, cross-environment validation, and subsystem health visualization across 6 key flight parameters from 63,964+ real flight records.

---

## Project Overview

This project analyzes real-world flight telemetry data from NASA's DASHlink dataset to detect sensor anomalies and assess subsystem health in avionics systems. The pipeline spans two environments:

- **Octave** — loading raw `.mat` flight recorder files and exporting structured CSV
- **Python** — data cleaning, statistical anomaly detection, visualization, and cross-validation

The methodology mirrors the data pipeline work carried out in defense aviation programs, where early anomaly detection is critical to flight safety and mission readiness.

---

## Dataset

| Property | Details |
|---|---|
| **Source** | NASA DASHlink — Sample Flight Data |
| **URL** | https://c3.ndc.nasa.gov/dashlink/projects/85/ |
| **Format** | `.mat` (MATLAB binary), one file per flight |
| **Aircraft** | 3 tail numbers (685, 652, 678) |
| **Total Records** | 63,964 |
| **Parameters available** | 186 sensor channels per flight |
| **Parameters used** | 6 (see below) |

### Parameters Analyzed

| Parameter | Field Names | Unit | Significance |
|---|---|---|---|
| Altitude | ALT / BALT | Feet | Primary navigation — altimeter health |
| Airspeed | CAS / IAS | Knots | Flight envelope monitoring — pitot tube |
| Pitch | PTCH / PITCH | Degrees | Longitudinal flight control |
| Roll | ROLL | Degrees | Lateral flight control |
| Engine N1 | N1 / N1L / N1R | % RPM | Engine health — most critical parameter |
| Temperature | TAT / SAT / OAT | °C | Environmental sensing — icing risk |


---


## Methodology

### Anomaly Detection

Two independent statistical methods are applied per channel:

**Z-Score**
```
Z = (X - mean) / std_dev
Flag if |Z| > 3
```
Best for normally distributed data. 99.7% of normal values fall within ±3 standard deviations.

**IQR (Interquartile Range)**
```
IQR = Q3 - Q1
Lower = Q1 - 1.5 × IQR
Upper = Q3 + 1.5 × IQR
Flag if value < Lower or value > Upper
```
More robust for skewed distributions — not affected by extreme values in the mean calculation.

**Combined Flag:** A reading is anomalous if flagged by **either** method (union / OR logic).

### Correlation Analysis

Pearson correlation computed between all 6 sensor channels to identify interdependencies. Expected correlations (e.g., altitude–airspeed, engine N1–temperature) serve as sanity checks. Unexpected correlations can indicate sensor drift or cross-system faults.

### Cross-Validation

The same correlation matrix is computed independently in Octave and Python. Element-wise absolute difference is calculated — a max difference near 0 confirms both environments processed the data consistently.

---

## Results

| Metric | Value |
|---|---|
| Total records processed | 63,964 |
| Aircraft tail numbers | 3 (685, 652, 678) |
| Anomaly detection methods | Z-score + IQR (combined) |
| Cross-validation max difference | < 0.01 |
| Visualizations produced | 4 |

**Key findings:**
- Altitude and Airspeed show positive correlation — consistent with aerodynamic behavior during climb/descent
- Engine N1 and Temperature show positive correlation — higher RPM generates more heat
- Z-score and IQR methods agreed on ~90%+ of flagged anomalies

---

## Visualizations

| Plot | Description |
|---|---|
| `timeseries_anomalies.png` | 6-panel time-series with red anomaly markers overlaid |
| `correlation_heatmap.png` | Pearson correlation matrix heatmap (6×6) |
| `anomaly_distribution.png` | Bar chart of anomaly counts per sensor channel |
| `health_kpi_dashboard.png` | Colour-coded subsystem health scores (green/orange/red) |

---


## References

- NASA DASHlink Flight Data: https://c3.ndc.nasa.gov/dashlink/projects/85/
- NASA DASHlink Anomaly Dataset: https://c3.ndc.nasa.gov/dashlink/resources/1018/

---

