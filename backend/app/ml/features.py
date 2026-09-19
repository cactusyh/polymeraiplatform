"""Repeat-unit structural features shared by training, prediction, and AD."""
from __future__ import annotations

import numpy as np
from rdkit import DataStructs

from backend.app.chemistry.service import FINGERPRINT_CONFIG, ChemistryProcessingError, fingerprint, process
from backend.app.ml.types import FeatureRow

DESCRIPTOR_KEYS = ("heavy_atom_count", "heteroatom_count", "ring_count", "aromatic_ring_count", "rotatable_bond_count", "fraction_csp3")
FEATURE_CONFIG = {"fingerprint": FINGERPRINT_CONFIG, "descriptor_keys": list(DESCRIPTOR_KEYS), "feature_version": "phase5-v1"}


def feature_row(representation_type: str, representation: str) -> FeatureRow:
    result = process(representation_type, representation)
    if result.status not in {"valid", "partially_valid"} or not result.normalized_representation:
        raise ChemistryProcessingError(result.validation_message or "Structure cannot generate features.")
    bit_vector = fingerprint(result.normalized_representation)
    bits = np.zeros(FINGERPRINT_CONFIG["n_bits"], dtype=np.float64)
    DataStructs.ConvertToNumpyArray(bit_vector, bits)
    descriptors = np.asarray([result.derived_properties[key] for key in DESCRIPTOR_KEYS], dtype=np.float64)
    return FeatureRow(result.normalized_representation, result.status, result.warnings, np.concatenate((bits, descriptors)))


def feature_matrix(rows: list[FeatureRow]) -> np.ndarray:
    return np.vstack([row.values for row in rows])
