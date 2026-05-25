"""Pytest fixtures and configuration."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_sensor_df():
    """Small synthetic sensor dataframe for tests."""
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        "unit_number": np.repeat([1, 2, 3, 4], 50),
        "time_in_cycles": np.tile(np.arange(50), 4),
        "op_setting_1": np.ones(n),
        "op_setting_2": np.zeros(n),
        "op_setting_3": np.zeros(n),
    })
    for i in range(1, 22):
        df[f"sensor_{i}"] = np.random.randn(n).cumsum() + 100
    df["RUL"] = np.tile(np.arange(50, 0, -1), 4)
    return df


@pytest.fixture
def sample_features():
    """Random feature matrix for model tests."""
    np.random.seed(42)
    return np.random.randn(100, 10)


@pytest.fixture
def sample_labels():
    """Random labels for regression tests."""
    np.random.seed(42)
    return np.random.randint(10, 200, size=100).astype(float)
