"""Prediction service independent of HTTP or frontend concerns."""
from backend.app.ml.applicability import similarity_summary
from backend.app.ml.features import feature_row
from backend.app.ml.registry import load_artifact
from backend.app.ml.uncertainty import interval

def predict(artifact_path, representation_type, representation):
 model,manifest,_=load_artifact(artifact_path); feature=feature_row(representation_type,representation); value=float(model.predict(feature.values.reshape(1,-1))[0]); return {"prediction":value,"uncertainty":interval(value,manifest.get("calibration_residual_quantile")),"applicability_domain":similarity_summary(feature.normalized_representation,manifest["training_normalized_representations"],manifest.get("applicability_threshold")),"structure":{"normalized_representation":feature.normalized_representation,"normalization_version":manifest["normalization_version"],"validation_status":feature.validation_status,"warnings":feature.warnings},"manifest":manifest}
