"""
Feature engineering and preprocessing for C-MAPSS data.
"""

from typing import List, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


SENSOR_COLS = [f"sensor_{i}" for i in range(1, 22)]
OP_COLS = ["op_setting_1", "op_setting_2", "op_setting_3"]
CONSTANT_SENSOR_THRESHOLD = 0.01


def drop_constant_sensors(df: pd.DataFrame, threshold: float = CONSTANT_SENSOR_THRESHOLD) -> List[str]:
    """Identify and return sensors with near-zero variance."""
    variances = df[SENSOR_COLS].var().sort_values()
    constant = variances[variances < threshold].index.tolist()
    return constant


def engineer_features(df: pd.DataFrame, sensors: List[str], window: int = 10) -> pd.DataFrame:
    """
    Engineer rolling-window and derivative features for each sensor.
    
    Features:
    - rolling mean (window=10)
    - rolling std (window=10)
    - first-order diff
    - normalized cycle position
    - operating setting sum
    """
    feature_df = df.copy()
    
    for sensor in sensors:
        # Rolling mean
        feature_df[f"{sensor}_rolling_mean"] = (
            feature_df.groupby("unit_number")[sensor]
            .rolling(window=window, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )
        # Rolling std
        feature_df[f"{sensor}_rolling_std"] = (
            feature_df.groupby("unit_number")[sensor]
            .rolling(window=window, min_periods=1)
            .std()
            .reset_index(level=0, drop=True)
        ).fillna(0)
        # First-order difference
        feature_df[f"{sensor}_diff"] = (
            feature_df.groupby("unit_number")[sensor]
            .diff()
            .fillna(0)
        )
    
    # Normalized cycle position (0=start, 1=end of life)
    feature_df["cycle_norm"] = feature_df.groupby("unit_number")["time_in_cycles"].transform(
        lambda x: x / x.max()
    )
    
    # Operating setting aggregate
    feature_df["op_setting_sum"] = feature_df[OP_COLS].sum(axis=1)
    
    return feature_df


class CMAPSSPreprocessor:
    """End-to-end preprocessor for C-MAPSS data."""
    
    def __init__(self, window: int = 10, scaler: Optional[StandardScaler] = None):
        self.window = window
        self.scaler = scaler or StandardScaler()
        self.useful_sensors: List[str] = []
        self.feature_cols: List[str] = []
        self._fitted = False
    
    def fit_transform(self, train_df: pd.DataFrame) -> pd.DataFrame:
        """Fit on training data and return transformed features."""
        # Drop constant sensors
        constant = drop_constant_sensors(train_df)
        self.useful_sensors = [s for s in SENSOR_COLS if s not in constant]
        print(f"Dropped {len(constant)} constant sensors, kept {len(self.useful_sensors)}")
        
        # Engineer features
        df = engineer_features(train_df, self.useful_sensors, self.window)
        
        # Build feature column list
        self.feature_cols = (
            self.useful_sensors
            + [f"{s}_rolling_mean" for s in self.useful_sensors]
            + [f"{s}_rolling_std" for s in self.useful_sensors]
            + [f"{s}_diff" for s in self.useful_sensors]
            + ["cycle_norm", "op_setting_sum"]
        )
        
        # Scale
        X = df[self.feature_cols].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        df_scaled = pd.DataFrame(X_scaled, columns=self.feature_cols, index=df.index)
        
        # Add metadata back
        for col in ["unit_number", "time_in_cycles", "RUL"]:
            if col in df.columns:
                df_scaled[col] = df[col].values
        
        self._fitted = True
        return df_scaled
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using fitted preprocessor."""
        if not self._fitted:
            raise RuntimeError("Preprocessor not fitted. Call fit_transform first.")
        
        df = engineer_features(df, self.useful_sensors, self.window)
        X = df[self.feature_cols].fillna(0)
        X_scaled = self.scaler.transform(X)
        df_scaled = pd.DataFrame(X_scaled, columns=self.feature_cols, index=df.index)
        
        for col in ["unit_number", "time_in_cycles"]:
            if col in df.columns:
                df_scaled[col] = df[col].values
        
        return df_scaled
