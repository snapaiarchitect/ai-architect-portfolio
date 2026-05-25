"""Tests for model classes."""

import numpy as np
import pandas as pd
import pytest

from src.models.anomaly_detector import AnomalyDetector
from src.models.rul_regressor import RULRegressor
from src.models.survival_model import SurvivalModel


class TestAnomalyDetector:
    def test_fit_and_predict(self, sample_features):
        """Detector should fit and predict."""
        det = AnomalyDetector(contamination=0.1, random_state=42)
        det.fit(sample_features)
        labels = det.predict(sample_features)
        assert len(labels) == len(sample_features)
        assert set(labels).issubset({-1, 1})

    def test_detect_adds_columns(self, sample_sensor_df):
        """detect() should add anomaly columns."""
        det = AnomalyDetector(contamination=0.1, random_state=42)
        df_out = det.detect(sample_sensor_df)
        assert "anomaly" in df_out.columns
        assert "anomaly_score" in df_out.columns
        assert df_out["anomaly"].dtype == bool

    def test_predict_before_fit_raises(self, sample_features):
        """Predict before fit should raise."""
        det = AnomalyDetector()
        with pytest.raises(RuntimeError):
            det.predict(sample_features)


class TestRULRegressor:
    def test_fit_and_predict(self, sample_features, sample_labels):
        """Regressor should fit and produce predictions."""
        reg = RULRegressor(random_state=42)
        reg.fit(sample_features, sample_labels)
        preds = reg.predict(sample_features)
        assert len(preds) == len(sample_features)
        assert np.isfinite(preds).all()

    def test_evaluate_returns_metrics(self, sample_features, sample_labels):
        """evaluate() should return standard metrics."""
        reg = RULRegressor(random_state=42)
        reg.fit(sample_features, sample_labels)
        metrics = reg.evaluate(sample_features, sample_labels)
        assert "MAE" in metrics
        assert "RMSE" in metrics
        assert "R2" in metrics
        assert metrics["n_samples"] == len(sample_features)


class TestSurvivalModel:
    def test_cox_fit(self):
        """Cox model should fit on synthetic survival data."""
        df = pd.DataFrame({
            "time_to_failure": np.random.exponential(100, 50),
            "failed": np.random.binomial(1, 0.5, 50),
            "age_years": np.random.rand(50),
            "condition_score": np.random.rand(50),
            "daily_usage_hours": np.random.rand(50),
            "days_since_maintenance": np.random.rand(50),
            "maintenance_frequency": np.random.rand(50),
            "criticality_encoded": np.random.randint(1, 5, 50),
        })
        model = SurvivalModel(model_type="cox")
        model.fit(df)
        assert model._fitted
        risks = model.predict_risk(df)
        assert len(risks) == len(df)
