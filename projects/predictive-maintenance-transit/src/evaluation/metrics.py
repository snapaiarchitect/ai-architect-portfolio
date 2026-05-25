"""
Evaluation metrics for predictive maintenance models.
"""

from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def c_index(y_true: np.ndarray, y_pred: np.ndarray, event_observed: np.ndarray) -> float:
    """
    Concordance index for survival predictions.
    
    Measures how well predicted risk ranks actual survival times.
    """
    concordant = 0
    permissible = 0
    n = len(y_true)
    
    for i in range(n):
        for j in range(i + 1, n):
            if event_observed[i] == 1 or event_observed[j] == 1:
                permissible += 1
                if (y_true[i] < y_true[j] and y_pred[i] < y_pred[j]) or \
                   (y_true[i] > y_true[j] and y_pred[i] > y_pred[j]):
                    concordant += 1
    
    return concordant / permissible if permissible > 0 else 0.5


def anomaly_validation(
    normal_group: pd.DataFrame,
    anomalous_group: pd.DataFrame,
    metric_col: str = "failure_count",
) -> Dict:
    """
    Validate anomaly detection by comparing with ground-truth outcomes.
    
    Returns t-test results and effect size.
    """
    normal_mean = normal_group[metric_col].mean()
    anomalous_mean = anomalous_group[metric_col].mean()
    
    t_stat, p_value = stats.ttest_ind(
        normal_group[metric_col],
        anomalous_group[metric_col],
        equal_var=False,
    )
    
    return {
        "normal_mean": float(normal_mean),
        "anomalous_mean": float(anomalous_mean),
        "ratio": float(anomalous_mean / normal_mean) if normal_mean > 0 else float("inf"),
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
    }


def forecast_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """Standard forecasting/regression metrics."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # Protected MAPE
    mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100
    
    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "R2": float(r2),
        "MAPE": float(mape),
    }


def print_metrics(metrics: Dict, title: str = "Model Performance") -> None:
    """Pretty-print metrics dict."""
    print(f"\n=== {title} ===")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        elif isinstance(value, bool):
            print(f"  {key}: {'YES' if value else 'NO'}")
        else:
            print(f"  {key}: {value}")
