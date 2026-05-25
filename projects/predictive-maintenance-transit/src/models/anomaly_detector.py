"""
Anomaly detection for sensor telemetry using Isolation Forest.
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:
    """
    Unsupervised anomaly detection for transit asset sensor data.
    
    Uses Isolation Forest with standardized features.
    """
    
    def __init__(
        self,
        contamination: float = 0.1,
        n_estimators: int = 200,
        random_state: int = 42,
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model: Optional[IsolationForest] = None
        self.scaler = StandardScaler()
        self.feature_names: Optional[List[str]] = None
        self._fitted = False
    
    def fit(self, X: np.ndarray, feature_names: Optional[List[str]] = None) -> "AnomalyDetector":
        """Fit Isolation Forest on training features."""
        X_scaled = self.scaler.fit_transform(X)
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.model.fit(X_scaled)
        self.feature_names = feature_names
        self._fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomaly labels (-1 = anomaly, 1 = normal)."""
        if not self._fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def score(self, X: np.ndarray) -> np.ndarray:
        """Get anomaly scores (lower = more anomalous)."""
        if not self._fitted:
            raise RuntimeError("Model not fitted.")
        X_scaled = self.scaler.transform(X)
        return self.model.decision_function(X_scaled)
    
    def detect(
        self,
        df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Run full anomaly detection pipeline on a DataFrame.
        
        Adds columns:
        - anomaly: bool
        - anomaly_score: float
        """
        if feature_cols is None:
            feature_cols = [
                c for c in df.select_dtypes(include=[np.number]).columns
                if c not in ["unit_number", "time_in_cycles", "RUL"]
            ]
        
        X = df[feature_cols].fillna(df[feature_cols].median()).values
        
        if not self._fitted:
            self.fit(X, feature_names=feature_cols)
        
        df = df.copy()
        df["anomaly"] = self.predict(X) == -1
        df["anomaly_score"] = self.score(X)
        return df
    
    def get_summary(self, df: pd.DataFrame) -> Dict:
        """Return anomaly detection summary statistics."""
        anomalies = df[df["anomaly"]]
        normal = df[~df["anomaly"]]
        return {
            "total_assets": len(df),
            "anomalous_assets": len(anomalies),
            "anomaly_rate": float(df["anomaly"].mean()),
            "normal_count": len(normal),
            "mean_anomaly_score_normal": float(normal["anomaly_score"].mean()),
            "mean_anomaly_score_anomalous": float(anomalies["anomaly_score"].mean()),
        }
