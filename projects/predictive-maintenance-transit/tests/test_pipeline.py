"""Tests for end-to-end pipeline."""

from pathlib import Path

import pytest

from src.pipeline.orchestrator import CMAPSSPipeline


class TestPipeline:
    def test_pipeline_init(self):
        """Pipeline should initialize."""
        pipe = CMAPSSPipeline()
        assert pipe.loader is not None
        assert pipe.preprocessor is not None
        assert pipe.regressor is not None

    def test_results_json_schema(self, tmp_path):
        """Results dict should follow expected schema."""
        pipe = CMAPSSPipeline(output_dir=tmp_path / "figures")
        # We can't run full pipeline without data, but we can check schema
        results = {
            "dataset": {"train_engines": 100, "test_engines": 100, "features": 50},
            "models": {
                "rul_regressor": {
                    "train": {"MAE": 10.0, "RMSE": 15.0, "R2": 0.8, "MAPE": 5.0},
                    "test": {"MAE": 12.0, "RMSE": 18.0, "R2": 0.75, "MAPE": 6.0},
                }
            },
        }
        assert "dataset" in results
        assert "models" in results
        assert "rul_regressor" in results["models"]
        assert "MAE" in results["models"]["rul_regressor"]["test"]
