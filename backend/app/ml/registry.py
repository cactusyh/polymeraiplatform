"""Filesystem model artifacts; database registry stores references and metadata."""
from __future__ import annotations
import json
from pathlib import Path
import joblib


def save_artifact(root: str | Path, property_key: str, version: str, model, manifest: dict, metrics: dict) -> Path:
    directory=Path(root)/property_key/version; directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, directory/"model.joblib")
    (directory/"manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (directory/"metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True))
    return directory


def load_artifact(path: str | Path):
    directory=Path(path)
    return joblib.load(directory/"model.joblib"), json.loads((directory/"manifest.json").read_text()), json.loads((directory/"metrics.json").read_text())
