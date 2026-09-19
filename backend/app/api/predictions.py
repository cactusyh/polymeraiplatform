import uuid
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models import MLModel, ModelPrediction, PropertyDefinition
from backend.app.ml.prediction import predict
from backend.app.schemas.prediction import PredictionRequest
router=APIRouter(prefix="/api/v1",tags=["predictions"])
def model_data(item): return {"id":str(item.id),"name":item.name,"version":item.version,"property_key":item.property_definition.key,"target_unit":item.target_unit,"model_type":item.model_type,"status":item.status,"training_dataset_name":item.training_dataset_name,"training_dataset_version":item.training_dataset_version,"feature_config":item.feature_config,"metrics":item.metrics,"manifest":item.manifest,"created_at":item.created_at}
@router.get("/models")
def models(db:Session=Depends(get_db)): return [model_data(x) for x in db.scalars(select(MLModel).join(MLModel.property_definition)).all()]
@router.get("/models/{model_id}")
def model(model_id:uuid.UUID,db:Session=Depends(get_db)):
 x=db.get(MLModel,model_id)
 if not x: raise HTTPException(404,"model not found")
 return model_data(x)
@router.post("/predictions")
def prediction(payload:PredictionRequest,db:Session=Depends(get_db)):
 definition=db.scalar(select(PropertyDefinition).where(PropertyDefinition.key==payload.property_key))
 if not definition: raise HTTPException(404,"property definition not found")
 query=select(MLModel).where(MLModel.property_definition_id==definition.id)
 if payload.model_id: query=query.where(MLModel.id==payload.model_id)
 else:
  active=db.scalars(query.where(MLModel.status=="active")).all()
  if len(active)!=1: raise HTTPException(409,"exactly one active model must be selected or provide model_id")
  item=active[0]
  query=None
 item=item if query is None else db.scalar(query)
 if not item: raise HTTPException(404,"no explicitly selected active model for property")
 try: result=predict(item.artifact_path,payload.representation_type,payload.representation)
 except Exception as error: raise HTTPException(422,"Structure cannot generate prediction features.") from error
 output={"property":{"key":definition.key,"unit":item.target_unit},"prediction":result["prediction"],"uncertainty":result["uncertainty"],"applicability_domain":result["applicability_domain"],"model":{"id":str(item.id),"name":item.name,"version":item.version,"model_type":item.model_type,"status":item.status,"not_for_scientific_use":item.status=="test"},"structure":result["structure"]}
 if payload.persist:
  saved=ModelPrediction(model_id=item.id,property_definition_id=definition.id,raw_representation=payload.representation,normalized_representation=result["structure"]["normalized_representation"],prediction_value=result["prediction"],target_unit=item.target_unit,uncertainty=result["uncertainty"],applicability_domain=result["applicability_domain"],feature_config=item.feature_config);db.add(saved);db.commit();output["prediction_id"]=str(saved.id)
 return output
