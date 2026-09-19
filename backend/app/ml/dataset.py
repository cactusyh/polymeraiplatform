"""Dataset contract, auditing, and leakage-safe grouped splitting."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from backend.app.chemistry.service import ChemistryProcessingError
from backend.app.ml.features import feature_row
from backend.app.ml.types import DatasetAudit, FeatureRow

REQUIRED_COLUMNS = {"representation", "representation_type", "property_key", "target_value", "target_unit"}


@dataclass(frozen=True)
class PreparedDataset:
    rows: pd.DataFrame
    features: list[FeatureRow]
    targets: np.ndarray
    audit: DatasetAudit


def load_dataset(path: str | Path, property_key: str, target_unit: str) -> PreparedDataset:
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Training dataset is missing required columns: {', '.join(sorted(missing))}")
    selected = frame[frame["property_key"] == property_key].copy()
    audit = {"input_rows": len(selected), "valid_rows": 0, "invalid_structures": 0, "unsupported_structures": 0, "missing_targets": 0, "non_finite_targets": 0, "incompatible_units": 0, "duplicate_structures": 0, "final_training_rows": 0}
    kept: list[dict] = []
    features: list[FeatureRow] = []
    for _, row in selected.iterrows():
        if pd.isna(row["target_value"]):
            audit["missing_targets"] += 1; continue
        try:
            target = float(row["target_value"])
        except (TypeError, ValueError):
            audit["non_finite_targets"] += 1; continue
        if not np.isfinite(target):
            audit["non_finite_targets"] += 1; continue
        if row["target_unit"] != target_unit:
            audit["incompatible_units"] += 1; continue
        try:
            feature = feature_row(str(row["representation_type"]), str(row["representation"]))
        except ChemistryProcessingError:
            if str(row["representation_type"]) not in {"smiles", "psmiles", "repeat_unit_smiles"}: audit["unsupported_structures"] += 1
            else: audit["invalid_structures"] += 1
            continue
        audit["valid_rows"] += 1
        kept.append({"target": target, "normalized_representation": feature.normalized_representation})
        features.append(feature)
    prepared = pd.DataFrame(kept)
    audit["duplicate_structures"] = int(prepared.duplicated("normalized_representation").sum()) if not prepared.empty else 0
    audit["final_training_rows"] = len(prepared)
    return PreparedDataset(prepared, features, prepared["target"].to_numpy(dtype=float), DatasetAudit(**audit))


def grouped_split(groups: np.ndarray, seed: int, test_fraction: float = .15, calibration_fraction: float = .15) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Split exact normalized structures into disjoint train/calibration/test groups."""
    if len(set(groups)) < 3: raise ValueError("At least three distinct normalized structures are required.")
    indices = np.arange(len(groups))
    first = GroupShuffleSplit(n_splits=1, test_size=test_fraction, random_state=seed)
    train_cal, test = next(first.split(indices, groups=groups))
    remaining_groups = groups[train_cal]
    calibration_relative = calibration_fraction / (1 - test_fraction)
    second = GroupShuffleSplit(n_splits=1, test_size=calibration_relative, random_state=seed + 1)
    train_relative, calibration_relative_indices = next(second.split(train_cal, groups=remaining_groups))
    train, calibration = train_cal[train_relative], train_cal[calibration_relative_indices]
    return train, calibration, test


def assert_no_group_leakage(groups: np.ndarray, splits: tuple[np.ndarray, np.ndarray, np.ndarray]) -> None:
    memberships = [set(groups[index]) for index in splits]
    if memberships[0] & memberships[1] or memberships[0] & memberships[2] or memberships[1] & memberships[2]:
        raise ValueError("Normalized structure leakage detected across train/calibration/test splits.")
