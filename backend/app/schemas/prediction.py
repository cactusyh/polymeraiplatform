import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
class PredictionRequest(BaseModel):
    model_config=ConfigDict(protected_namespaces=())
    property_key:str; representation_type:str; representation:str=Field(min_length=1,max_length=4096); model_id:uuid.UUID|None=None; persist:bool=False
class ModelRead(BaseModel):
    model_config=ConfigDict(protected_namespaces=())
    id:str;name:str;version:str;property_key:str;target_unit:str;model_type:str;status:str;training_dataset_name:str;training_dataset_version:str|None;feature_config:dict;metrics:dict;manifest:dict;created_at:datetime
