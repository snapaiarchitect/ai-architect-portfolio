"""Tests for data loading and preprocessing."""

import numpy as np
import pandas as pd
import pytest

from src.data.loader import NASACMAPSSLoader
from src.data.preprocessor import CMAPSSPreprocessor, drop_constant_sensors, engineer_features


class TestPreprocessor:
    def test_drop_constant_sensors(self, sample_sensor_df):
        """Constant sensors should be identified."""
        # Make sensor_1 constant
        sample_sensor_df["sensor_1"] = 5.0
        constant = drop_constant_sensors(sample_sensor_df, threshold=0.01)
        assert "sensor_1" in constant

    def test_engineer_features_shape(self, sample_sensor_df):
        """Feature engineering should expand column count."""
        sensors = [f"sensor_{i}" for i in range(1, 22)]
        df_out = engineer_features(sample_sensor_df, sensors, window=10)
        assert "cycle_norm" in df_out.columns
        assert "op_setting_sum" in df_out.columns
        assert f"{sensors[0]}_rolling_mean" in df_out.columns

    def test_preprocessor_fit_transform(self, sample_sensor_df):
        """Preprocessor should scale and return features."""
        prep = CMAPSSPreprocessor(window=10)
        df_out = prep.fit_transform(sample_sensor_df)
        assert prep._fitted
        assert len(prep.feature_cols) > 0
        assert "cycle_norm" in df_out.columns
        # Values should be roughly zero-mean, unit-var after scaling
        feature_cols = [c for c in df_out.columns if c not in ["unit_number", "time_in_cycles", "RUL"]]
        means = df_out[feature_cols].mean().abs()
        assert (means < 2.0).all()

    def test_preprocessor_transform_without_fit_raises(self, sample_sensor_df):
        """Transform before fit should raise."""
        prep = CMAPSSPreprocessor()
        with pytest.raises(RuntimeError):
            prep.transform(sample_sensor_df)


class TestLoader:
    def test_loader_init(self):
        """Loader should initialize with correct paths."""
        loader = NASACMAPSSLoader()
        assert loader.data_dir.name == "raw"
