# Predictive Maintenance for Transit Systems

[![CI](https://github.com/snapaiarchitect/ai-architect-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/snapaiarchitect/ai-architect-portfolio/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **End-to-end ML pipeline** for predicting Remaining Useful Life (RUL) of turbofan engines using the NASA C-MAPSS dataset. Includes anomaly detection, survival analysis, and an interactive Streamlit dashboard.

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Raw Data   │────▶│  Feature    │────▶│   Models    │
│  (NASA)     │     │ Engineering │     │  RF + XGB   │
└─────────────┘     └─────────────┘     └─────────────┘
                                                 │
                          ┌──────────────────────┘
                          ▼
                   ┌─────────────┐
                   │  Evaluation │
                   │  MAE, RMSE  │
                   └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Dashboard   │
                   │  Streamlit  │
                   └─────────────┘
```

## Quick Start

```bash
# Install
make install

# Download NASA C-MAPSS data
make fetch

# Run full pipeline
make run

# Launch dashboard
make dashboard

# Run tests
make test
```

## Dataset

**NASA C-MAPSS FD001** — Commercial Modular Aero-Propulsion System Simulation

- **100 training engines**: run-to-failure trajectories
- **100 test engines**: truncated before failure
- **26 columns**: unit ID, cycle, 3 operating settings, 21 sensor measurements
- **Real simulation data** — no synthetic generation

Source: [NASA Prognostics Center of Excellence](https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/)

## Project Structure

```
├── src/
│   ├── data/           # Loading, feature engineering
│   ├── models/         # Anomaly detection, survival, RUL regression
│   ├── evaluation/     # Metrics: c-index, MAE, RMSE, R²
│   ├── pipeline/       # End-to-end orchestrator
│   └── visualization/ # Plots + Streamlit dashboard
├── tests/              # pytest suite with fixtures
├── notebooks/          # Exploratory analysis
├── figures/            # Generated outputs
└── docs/               # Project detail page (GitHub Pages)
```

## Results

| Metric | Training | Test |
|--------|----------|------|
| MAE (cycles) | ~10.0 | ~12.0 |
| RMSE | ~15.0 | ~18.0 |
| R² | 0.80 | 0.75 |

## Interactive Charts

- [Sensor Degradation Curves](../../charts/sensor_degradation.html)
- [Ensemble Forecast](../../charts/ensemble_forecast.html)
- [WMATA Ridership](../../charts/wmata_ridership.html)

## License

MIT © Sierra Napier
