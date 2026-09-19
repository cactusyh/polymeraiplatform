"""Split-conformal prediction intervals."""
from __future__ import annotations
import numpy as np


def calibrate_residual_quantile(y_true: np.ndarray, prediction: np.ndarray, coverage: float = .90) -> float | None:
    if len(y_true) < 5: return None
    residuals = np.sort(np.abs(y_true - prediction))
    rank = min(len(residuals) - 1, int(np.ceil((len(residuals) + 1) * coverage)) - 1)
    return float(residuals[rank])


def interval(value: float, residual_quantile: float | None, coverage: float = .90) -> dict | None:
    if residual_quantile is None: return None
    return {"method": "split_conformal", "coverage": coverage, "lower": value - residual_quantile, "upper": value + residual_quantile}
