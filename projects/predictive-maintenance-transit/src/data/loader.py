"""
Data loading and acquisition for NASA C-MAPSS turbofan engine dataset.

Source: NASA Prognostics Center of Excellence
https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/
"""

import os
import zipfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.request import urlretrieve

import pandas as pd


NASA_CMAPSS_URL = "https://ti.arc.nasa.gov/c/6/"
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"


def download_cmapss_dataset(dest_dir: Optional[Path] = None, force: bool = False) -> Path:
    """Download NASA C-MAPSS FD001 dataset if not present."""
    dest = Path(dest_dir) if dest_dir else DATA_DIR
    dest.mkdir(parents=True, exist_ok=True)
    
    train_file = dest / "train_FD001.txt"
    test_file = dest / "test_FD001.txt"
    rul_file = dest / "RUL_FD001.txt"
    
    if all(f.exists() for f in [train_file, test_file, rul_file]) and not force:
        print("C-MAPSS FD001 data already present.")
        return dest
    
    # NASA data is distributed via direct file links
    print("Downloading NASA C-MAPSS FD001 dataset...")
    
    base_url = "https://raw.githubusercontent.com/sisifos1/NASA-C-MAPSS/main/CMAPSSData/"
    
    files = {
        "train_FD001.txt": f"{base_url}train_FD001.txt",
        "test_FD001.txt": f"{base_url}test_FD001.txt",
        "RUL_FD001.txt": f"{base_url}RUL_FD001.txt",
    }
    
    for fname, url in files.items():
        fpath = dest / fname
        if not fpath.exists() or force:
            print(f"  Downloading {fname}...")
            try:
                urlretrieve(url, fpath)
            except Exception as e:
                print(f"  Warning: could not download {fname}: {e}")
                print(f"  Please download manually from NASA repository.")
    
    return dest


class NASACMAPSSLoader:
    """Loader for NASA C-MAPSS FD001 dataset."""
    
    COL_NAMES = (
        ["unit_number", "time_in_cycles", "op_setting_1", "op_setting_2", "op_setting_3"]
        + [f"sensor_{i}" for i in range(1, 22)]
    )
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.train_df: Optional[pd.DataFrame] = None
        self.test_df: Optional[pd.DataFrame] = None
        self.true_rul: Optional[pd.Series] = None
    
    def load(self, download: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
        """Load train, test, and RUL data."""
        if download:
            download_cmapss_dataset(self.data_dir)
        
        train_path = self.data_dir / "train_FD001.txt"
        test_path = self.data_dir / "test_FD001.txt"
        rul_path = self.data_dir / "RUL_FD001.txt"
        
        if not train_path.exists():
            raise FileNotFoundError(
                f"Training data not found at {train_path}. "
                "Run download_cmapss_dataset() first."
            )
        
        self.train_df = pd.read_csv(
            train_path, sep=r"\s+", header=None, names=self.COL_NAMES
        )
        self.test_df = pd.read_csv(
            test_path, sep=r"\s+", header=None, names=self.COL_NAMES
        )
        self.true_rul = pd.read_csv(rul_path, header=None, names=["RUL"]).squeeze()
        
        print(f"Train: {self.train_df.shape[0]:,} rows, {self.train_df.shape[1]} columns")
        print(f"Test: {self.test_df.shape[0]:,} rows, {self.test_df.shape[1]} columns")
        print(f"True RUL: {len(self.true_rul)} engines")
        
        return self.train_df, self.test_df, self.true_rul
    
    def compute_rul(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute Remaining Useful Life for each cycle."""
        max_cycles = df.groupby("unit_number")["time_in_cycles"].max().reset_index()
        max_cycles.columns = ["unit_number", "max_cycle"]
        df = df.merge(max_cycles, on="unit_number")
        df["RUL"] = df["max_cycle"] - df["time_in_cycles"]
        df = df.drop("max_cycle", axis=1)
        return df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Download dataset")
    args = parser.parse_args()
    
    if args.download:
        download_cmapss_dataset()
    else:
        loader = NASACMAPSSLoader()
        loader.load()
