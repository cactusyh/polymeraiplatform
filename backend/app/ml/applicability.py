"""Dataset-relative structural familiarity assessment."""
from __future__ import annotations
import numpy as np
from rdkit import DataStructs
from backend.app.chemistry.service import fingerprint


def similarity_summary(normalized: str, training_normalized: list[str], threshold: float | None) -> dict:
    query = fingerprint(normalized)
    scores = sorted((DataStructs.TanimotoSimilarity(query, fingerprint(item)) for item in training_normalized), reverse=True)
    nearest = float(scores[0]) if scores else 0.0
    return {"nearest_training_similarity": nearest, "top_k_mean_similarity": float(np.mean(scores[:min(5, len(scores))])) if scores else 0.0, "reference_domain_threshold": threshold, "status": "within_reference_domain" if threshold is None or nearest >= threshold else "outside_reference_domain", "method": "maximum_tanimoto_similarity_to_training_structures"}


def training_threshold(training_normalized: list[str]) -> float | None:
    if len(training_normalized) < 3: return None
    values=[]
    for index, item in enumerate(training_normalized):
        others=training_normalized[:index]+training_normalized[index+1:]
        values.append(similarity_summary(item, others, None)["nearest_training_similarity"])
    return float(np.quantile(values, .05))
