"""
End-to-end pipeline: load -> preprocess -> train -> evaluate -> visualize.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from ..data.loader import NASACMAPSSLoader
from ..data.preprocessor import CMAPSSPreprocessor
from ..models.rul_regressor import RULRegressor
from ..evaluation.metrics import forecast_metrics, print_metrics
from ..visualization.plots import save_sensor_degradation_plot, save_rul_distribution_plot


class CMAPSSPipeline:
    """
    Full pipeline for NASA C-MAPSS RUL prediction.
    
    Steps:
    1. Load raw data
    2. Compute RUL labels
    3. Engineer features + scale
    4. Train RUL regressor (RF + XGBoost ensemble)
    5. Evaluate on test set
    6. Generate plots
    7. Save results.json
    """
    
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        window: int = 10,
    ):
        self.data_dir = data_dir
        self.output_dir = Path(output_dir) if output_dir else Path("figures")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.window = window
        
        self.loader = NASACMAPSSLoader(data_dir)
        self.preprocessor = CMAPSSPreprocessor(window=window)
        self.regressor = RULRegressor()
        
        self.train_df: Optional[pd.DataFrame] = None
        self.test_df: Optional[pd.DataFrame] = None
        self.true_rul: Optional[pd.Series] = None
        self.results: Dict = {}
    
    def run(self, download: bool = True) -> Dict:
        """Execute full pipeline."""
        print("=" * 60)
        print("C-MAPSS Predictive Maintenance Pipeline")
        print("=" * 60)
        
        # 1. Load
        print("\n[1/6] Loading data...")
        raw_train, raw_test, self.true_rul = self.loader.load(download=download)
        self.train_df = self.loader.compute_rul(raw_train)
        self.test_df = raw_test.copy()
        
        # 2. Preprocess
        print("\n[2/6] Engineering features...")
        train_processed = self.preprocessor.fit_transform(self.train_df)
        
        # 3. Prepare matrices
        print("\n[3/6] Preparing train/test matrices...")
        feature_cols = [c for c in train_processed.columns if c not in ["unit_number", "time_in_cycles", "RUL"]]
        X_train = train_processed[feature_cols].fillna(0).values
        y_train = train_processed["RUL"].values
        
        # For test: use last cycle per engine (standard C-MAPSS protocol)
        test_last = self.test_df.groupby("unit_number").last().reset_index()
        test_processed = self.preprocessor.transform(test_last)
        X_test = test_processed[feature_cols].fillna(0).values
        y_test = self.true_rul.values
        
        # 4. Train
        print("\n[4/6] Training ensemble regressor...")
        self.regressor.fit(X_train, y_train)
        
        # 5. Evaluate
        print("\n[5/6] Evaluating...")
        train_metrics = self.regressor.evaluate(X_train, y_train)
        test_metrics = self.regressor.evaluate(X_test, y_test)
        
        print_metrics(train_metrics, "Training Performance")
        print_metrics(test_metrics, "Test Performance")
        
        self.results = {
            "dataset": {
                "train_engines": int(self.train_df["unit_number"].nunique()),
                "test_engines": int(self.test_df["unit_number"].nunique()),
                "features": len(feature_cols),
            },
            "models": {
                "rul_regressor": {
                    "train": train_metrics,
                    "test": test_metrics,
                }
            },
            "preprocessing": {
                "window": self.window,
                "scaler": "StandardScaler",
                "features": feature_cols[:10] + ["..."],  # truncated
            },
        }
        
        # 6. Visualize
        print("\n[6/6] Generating plots...")
        save_rul_distribution_plot(self.train_df, self.output_dir / "rul_distribution.png")
        save_sensor_degradation_plot(
            self.train_df,
            sample_engines=[1, 25, 50, 75],
            output_path=self.output_dir / "sensor_degradation.png",
        )
        
        # 7. Save results
        results_path = self.output_dir / ".." / "results.json"
        with open(results_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to {results_path}")
        
        return self.results


if __name__ == "__main__":
    pipeline = CMAPSSPipeline()
    pipeline.run()
