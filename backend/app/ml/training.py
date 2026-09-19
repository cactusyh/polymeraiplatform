"""Explicit CLI for a reproducible structure-only baseline training run."""
from __future__ import annotations
import argparse, platform, uuid
from datetime import datetime, timezone
import sklearn
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from backend.app.chemistry.service import FINGERPRINT_CONFIG, NORMALIZATION_VERSION
from backend.app.ml.applicability import training_threshold
from backend.app.ml.dataset import assert_no_group_leakage, grouped_split, load_dataset
from backend.app.ml.features import FEATURE_CONFIG, feature_matrix
from backend.app.ml.registry import save_artifact
from backend.app.ml.uncertainty import calibrate_residual_quantile
from backend.app.db.session import SessionLocal
from backend.app.models import MLModel, PropertyDefinition

def train(dataset_path, property_key, target_unit, artifact_root="models", seed=42):
    data=load_dataset(dataset_path,property_key,target_unit); groups=data.rows.normalized_representation.to_numpy(); splits=grouped_split(groups,seed); assert_no_group_leakage(groups,splits)
    train_i, cal_i, test_i=splits; X=feature_matrix(data.features); y=data.targets
    candidates={"ridge":Ridge(alpha=1.0),"extra_trees":ExtraTreesRegressor(n_estimators=100,random_state=seed,min_samples_leaf=1)}
    results={}
    for name, model in candidates.items():
        model.fit(X[train_i],y[train_i]); pred=model.predict(X[test_i]); results[name]={"mae":float(mean_absolute_error(y[test_i],pred)),"rmse":float(mean_squared_error(y[test_i],pred)**.5),"r2":float(r2_score(y[test_i],pred)),"n_train":len(train_i),"n_calibration":len(cal_i),"n_test":len(test_i)}
    selected=min(results,key=lambda name:results[name]["mae"]); model=candidates[selected]; residual=calibrate_residual_quantile(y[cal_i],model.predict(X[cal_i]))
    version="test-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest={"name":"synthetic software-test model — not for scientific use","version":version,"property_key":property_key,"target_unit":target_unit,"model_type":selected,"status":"test","training_dataset_name":"synthetic_test_fixture_not_scientific_data","training_dataset_version":"phase5-v1","random_seed":seed,"feature_config":FEATURE_CONFIG,"fingerprint_config":FINGERPRINT_CONFIG,"normalization_version":NORMALIZATION_VERSION,"sklearn_version":sklearn.__version__,"python_version":platform.python_version(),"created_at":datetime.now(timezone.utc).isoformat(),"split_strategy":"grouped by normalized_representation; train/calibration/test","calibration_residual_quantile":residual,"applicability_threshold":training_threshold(list(groups[train_i])),"training_normalized_representations":list(groups[train_i]),"dataset_audit":data.audit.as_dict()}
    path=save_artifact(artifact_root,property_key,version,model,manifest,{"candidates":results,"selected":selected,"held_out_test":results[selected]}); return path,manifest,results[selected]
def register_model(path, manifest, metrics):
    """Persist only artifact metadata; sklearn objects remain on the filesystem."""
    db=SessionLocal()
    try:
        definition=db.query(PropertyDefinition).filter_by(key=manifest["property_key"]).one()
        item=MLModel(name=manifest["name"],version=manifest["version"],property_definition_id=definition.id,target_unit=manifest["target_unit"],model_type=manifest["model_type"],status=manifest["status"],artifact_path=str(path),training_dataset_name=manifest["training_dataset_name"],training_dataset_version=manifest["training_dataset_version"],feature_config=manifest["feature_config"],metrics=metrics,manifest=manifest)
        db.add(item);db.commit();return item.id
    except Exception:
        db.rollback();raise
    finally:
        db.close()

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--dataset",required=True);p.add_argument("--property-key",required=True);p.add_argument("--target-unit",required=True);p.add_argument("--artifact-root",default="models");p.add_argument("--register",action="store_true");a=p.parse_args();path,manifest,metrics=train(a.dataset,a.property_key,a.target_unit,a.artifact_root);print(register_model(path,manifest,metrics) if a.register else path)
