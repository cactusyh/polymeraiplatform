"""Phase 5 structure-only prediction architecture tests (synthetic data only)."""
from pathlib import Path
import numpy as np
import pytest
from backend.app.ml.applicability import training_threshold
from backend.app.ml.dataset import assert_no_group_leakage, grouped_split, load_dataset
from backend.app.ml.features import feature_row
from backend.app.ml.registry import load_artifact
from backend.app.ml.training import train
from backend.app.ml.uncertainty import calibrate_residual_quantile, interval

FIXTURE=Path(__file__).parent/"fixtures"/"synthetic_test_fixture_not_scientific_data.csv"
def test_features_audit_and_grouped_no_leakage():
 assert feature_row("psmiles","[*]CC[*]").values.shape==(2054,)
 data=load_dataset(FIXTURE,"density","g/cm^3"); assert data.audit.final_training_rows==12
 groups=data.rows.normalized_representation.to_numpy(); splits=grouped_split(groups,42); assert_no_group_leakage(groups,splits)
 with pytest.raises(ValueError): assert_no_group_leakage(np.array(["a","a","b"]),(np.array([0]),np.array([1]),np.array([2])))
def test_training_artifact_manifest_and_uncertainty(tmp_path):
 path,manifest,metrics=train(FIXTURE,"density","g/cm^3",tmp_path,seed=42)
 model,loaded_manifest,loaded_metrics=load_artifact(path)
 assert model is not None and loaded_manifest==manifest and loaded_metrics["selected"] in {"ridge","extra_trees"}
 assert manifest["status"]=="test" and "not for scientific use" in manifest["name"]
 assert metrics["n_train"]+metrics["n_calibration"]+metrics["n_test"]==12
 assert interval(1.0,calibrate_residual_quantile(np.arange(5),np.arange(5)+.1)) is not None
 assert calibrate_residual_quantile(np.arange(4),np.arange(4)) is None
 assert training_threshold(manifest["training_normalized_representations"]) is not None


def test_prediction_api_and_model_card(client, db_session, tmp_path):
    from backend.app.models import MLModel, PropertyDefinition
    path, manifest, metrics = train(FIXTURE, "density", "g/cm^3", tmp_path)
    definition = PropertyDefinition(key="density", name="Density", canonical_unit="g/cm^3")
    db_session.add(definition); db_session.commit()
    item = MLModel(name=manifest["name"], version=manifest["version"], property_definition_id=definition.id, target_unit="g/cm^3", model_type=manifest["model_type"], status="test", artifact_path=str(path), training_dataset_name=manifest["training_dataset_name"], training_dataset_version="phase5-v1", feature_config=manifest["feature_config"], metrics=metrics, manifest=manifest)
    db_session.add(item); db_session.commit()
    response = client.post("/api/v1/predictions", json={"property_key":"density", "representation_type":"psmiles", "representation":"[*]CC[*]", "model_id":str(item.id)})
    assert response.status_code == 200
    assert response.json()["model"]["not_for_scientific_use"] is True
    assert "nearest_training_similarity" in response.json()["applicability_domain"]
    assert client.post("/api/v1/predictions", json={"property_key":"density", "representation_type":"smiles", "representation":"invalid", "model_id":str(item.id)}).status_code == 422
    assert client.get("/api/v1/models/" + str(item.id)).status_code == 200
