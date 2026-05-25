"""
Streamlit dashboard for interactive exploration of results.
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Predictive Maintenance — NASA C-MAPSS",
    layout="wide",
)

st.title("🔧 Predictive Maintenance Dashboard")
st.caption("NASA C-MAPSS Turbofan Engine Degradation Analysis")


def load_results():
    """Load results.json and data files if present."""
    results_path = Path("results.json")
    if results_path.exists():
        with open(results_path) as f:
            return json.load(f)
    return None


results = load_results()

if results:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Train Engines", results["dataset"]["train_engines"])
    col2.metric("Test Engines", results["dataset"]["test_engines"])
    col3.metric("Features", results["dataset"]["features"])
    
    test_mae = results["models"]["rul_regressor"]["test"]["MAE"]
    col4.metric("Test MAE (cycles)", f"{test_mae:.1f}")
    
    st.subheader("Model Performance")
    train_metrics = results["models"]["rul_regressor"]["train"]
    test_metrics = results["models"]["rul_regressor"]["test"]
    
    col_t, col_v = st.columns(2)
    with col_t:
        st.markdown("**Training**")
        st.json(train_metrics)
    with col_v:
        st.markdown("**Test**")
        st.json(test_metrics)
    
    # Show generated plots
    fig_dir = Path("figures")
    if fig_dir.exists():
        st.subheader("Visualizations")
        for img in sorted(fig_dir.glob("*.png")):
            st.image(str(img), caption=img.stem.replace("_", " ").title())
else:
    st.info("Run the pipeline first to generate results:")
    st.code("python -m src.pipeline.orchestrator", language="bash")

st.sidebar.markdown("---")
st.sidebar.caption("Sierra Napier · AI Architect & Data Science Leader")
