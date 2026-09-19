# Phase 5 Property Prediction

## Real-data status

**SYNTHETIC SOFTWARE-TEST MODEL ONLY.** The repository contains no curated scientific training dataset. The included small synthetic test fixture is for software verification only. Models trained from it have status test and are not for scientific use.

## Feature representation

Phase 5 reuses the Phase 4 chemistry service: attachment-aware Morgan fingerprints (radius 2, 2048 bits, wildcards retained) plus repeat-unit graph descriptors. These are not complete polymer-material features.

## Dataset, splits, and metrics

Input requires representation, representation type, property key, target value, and target unit. The audit reports missing/non-finite targets, invalid/unsupported structures, unit mismatches, duplicates, and final rows. Runs use a single explicit unit. Reproducible train/calibration/test splitting groups by normalized representation, preventing exact-structure leakage. Ridge and ExtraTrees are evaluated with held-out MAE, RMSE, R2, and sample counts.

## Uncertainty and applicability

Split conformal intervals are calibrated only on the reserved calibration set; insufficient calibration returns unavailable. Applicability returns maximum and top-k Tanimoto similarity to training structures and a low-tail, dataset-relative threshold. It is not a guarantee of accuracy.

## Registry, provenance, and limitations

Artifacts live outside the database under models/property/version with model, manifest, and metrics. The registry retains metadata and paths only. ModelPrediction remains separate from experimental PropertyRecord and is persisted only on explicit request. Structure-only prediction does not encode Mn, Mw, dispersity, DP, processing, morphology, crystallinity, formulation, topology, or measurement conditions unless future models explicitly include them.
