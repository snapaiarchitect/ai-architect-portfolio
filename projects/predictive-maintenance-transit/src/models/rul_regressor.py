"""
Remaining Useful Life (RUL) regression models.

Random Forest + XGBoost ensemble for turbofan engine degradation.
"""

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb


class RULRegressor:
    """
    Ensemble regressor for RUL prediction.
    
    Trains both Random Forest and XGBoost, then blends predictions.
    """
    
    def __init__(
        self,
        rf_params: Optional[Dict] = None,
        xgb_params: Optional[Dict] = None,
        blend_weights: Tuple[float, float] = (0.5, 0.5),
    ):
        self.rf_params = rf_params or {
            "n_estimators": 200,
            "max_depth": 10,
            "random_state": 42,
            "n_jobs": -1,
        }
        self.xgb_params = xgb_params or {
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
        }
        self.blend_weights = blend_weights
        self.rf_model: Optional[RandomForestRegressor] = None
        self.xgb_model: Optional[xgb.XGBRegressor] = None
        self.scaler = StandardScaler()
        self._fitted = False
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "RULRegressor":
        """Fit both models."""
        X_scaled = self.scaler.fit_transform(X)
        
        self.rf_model = RandomForestRegressor(**self.rf_params)
        self.rf_model.fit(X_scaled, y)
        
        self.xgb_model = xgb.XGBRegressor(**self.xgb_params)
        self.xgb_model.fit(X_scaled, y)
        
        self._fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Blended prediction from both models."""
        if not self._fitted:
            raise RuntimeError("Model not fitted.")
        X_scaled = self.scaler.transform(X)
        rf_pred = self.rf_model.predict(X_scaled)
        xgb_pred = self.xgb_model.predict(X_scaled)
        w1, w2 = self.blend_weights
        return w1 * rf_pred + w2 * xgb_pred
    
    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> Dict:
        """Return standard regression metrics."""
        y_pred = self.predict(X)
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        
        # MAPE with protection against zero
        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100
        
        return {
            "MAE": float(mae),
            "RMSE": float(rmse),
            "R2": float(r2),
            "MAPE": float(mape),
            "n_samples": len(y_true),
        }
