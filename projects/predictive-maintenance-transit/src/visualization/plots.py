"""
Static plot generation for C-MAPSS analysis.
"""

from pathlib import Path
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 10


def save_rul_distribution_plot(df: pd.DataFrame, output_path: Path) -> None:
    """Plot training RUL and engine lifetime distributions."""
    engine_lifetimes = df.groupby("unit_number")["time_in_cycles"].max()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(df["RUL"], bins=50, color="steelblue", edgecolor="white")
    axes[0].set_xlabel("Remaining Useful Life (cycles)")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Training RUL Distribution")
    
    axes[1].hist(engine_lifetimes, bins=20, color="coral", edgecolor="white")
    axes[1].set_xlabel("Engine Lifetime (cycles)")
    axes[1].set_ylabel("Count")
    axes[1].set_title("Engine Failure Time Distribution")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def save_sensor_degradation_plot(
    df: pd.DataFrame,
    sample_engines: List[int],
    output_path: Path,
    sensors: Optional[List[str]] = None,
) -> None:
    """Plot sensor degradation curves for sample engines."""
    if sensors is None:
        sensors = [f"sensor_{i}" for i in range(1, 22)]
    
    n_sensors = len(sensors)
    n_cols = 7
    n_rows = int(np.ceil(n_sensors / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 3 * n_rows))
    axes = axes.flatten()
    
    for idx, sensor in enumerate(sensors):
        ax = axes[idx]
        for engine in sample_engines:
            engine_data = df[df["unit_number"] == engine]
            ax.plot(
                engine_data["time_in_cycles"],
                engine_data[sensor],
                alpha=0.7,
                label=f"Engine {engine}",
            )
        ax.set_title(sensor, fontsize=9)
        ax.set_xlabel("Cycle", fontsize=8)
        ax.tick_params(labelsize=7)
        if idx == 0:
            ax.legend(fontsize=7, loc="upper left")
    
    # Hide unused subplots
    for idx in range(n_sensors, len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle("Sensor Degradation Curves", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_feature_importance(model, feature_names: List[str], output_path: Path, top_n: int = 20) -> None:
    """Plot top-N feature importances from a tree-based model."""
    if not hasattr(model, "feature_importances_"):
        print("Model does not expose feature_importances_")
        return
    
    importances = model.feature_importances_
    indices = np.argsort(importances)[-top_n:]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(top_n), importances[indices], color="teal")
    ax.set_yticks(range(top_n))
    ax.set_yticklabels([feature_names[i] for i in indices])
    ax.set_xlabel("Importance")
    ax.set_title(f"Top {top_n} Feature Importances")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")
