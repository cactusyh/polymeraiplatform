"""Typed contracts for property-prediction training and inference."""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DatasetAudit:
    input_rows: int
    valid_rows: int
    invalid_structures: int
    unsupported_structures: int
    missing_targets: int
    non_finite_targets: int
    incompatible_units: int
    duplicate_structures: int
    final_training_rows: int

    def as_dict(self) -> dict[str, int]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class FeatureRow:
    normalized_representation: str
    validation_status: str
    warnings: list[str]
    values: Any
