"""
Survival analysis models: Kaplan-Meier, Cox PH, and Weibull.
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter, WeibullFitter
from lifelines.statistics import logrank_test


class SurvivalModel:
    """
    Wrapper for survival analysis models on asset failure data.
    
    Supports Cox Proportional Hazards, Kaplan-Meier, and Weibull.
    """
    
    MODELS = ["cox", "kaplan_meier", "weibull"]
    
    def __init__(self, model_type: str = "cox"):
        if model_type not in self.MODELS:
            raise ValueError(f"model_type must be one of {self.MODELS}")
        self.model_type = model_type
        self.model = None
        self.feature_cols: Optional[List[str]] = None
        self._fitted = False
    
    def fit(
        self,
        df: pd.DataFrame,
        duration_col: str = "time_to_failure",
        event_col: str = "failed",
        feature_cols: Optional[List[str]] = None,
    ) -> "SurvivalModel":
        """Fit survival model."""
        if feature_cols is None:
            feature_cols = [
                "age_years",
                "condition_score",
                "daily_usage_hours",
                "days_since_maintenance",
                "maintenance_frequency",
                "criticality_encoded",
            ]
        self.feature_cols = feature_cols
        
        df_fit = df[feature_cols + [duration_col, event_col]].copy()
        df_fit[duration_col] = df_fit[duration_col] / 365.25  # days -> years
        df_fit = df_fit.dropna()
        
        if self.model_type == "cox":
            self.model = CoxPHFitter(penalizer=0.01)
            self.model.fit(df_fit, duration_col=duration_col, event_col=event_col)
        elif self.model_type == "weibull":
            self.model = WeibullFitter()
            self.model.fit(df_fit[duration_col], event_observed=df_fit[event_col])
        elif self.model_type == "kaplan_meier":
            self.model = KaplanMeierFitter()
            self.model.fit(df_fit[duration_col], event_observed=df_fit[event_col])
        
        self._fitted = True
        return self
    
    def predict_risk(self, df: pd.DataFrame) -> np.ndarray:
        """Predict risk scores (higher = more likely to fail)."""
        if not self._fitted:
            raise RuntimeError("Model not fitted.")
        if self.model_type == "cox":
            return self.model.predict_partial_hazard(df[self.feature_cols]).values
        return np.ones(len(df))
    
    def predict_survival(self, times: np.ndarray) -> np.ndarray:
        """Predict survival function S(t) at given times."""
        if not self._fitted:
            raise RuntimeError("Model not fitted.")
        if self.model_type in ["kaplan_meier", "weibull"]:
            return self.model.survival_function_at_times(times).values
        return np.ones(len(times))
    
    def summary(self) -> Dict:
        """Return model summary statistics."""
        if not self._fitted:
            raise RuntimeError("Model not fitted.")
        return {
            "model_type": self.model_type,
            "fitted": True,
            "log_likelihood": getattr(self.model, "log_likelihood_", None),
            "AIC": getattr(self.model, "AIC_", None),
        }
