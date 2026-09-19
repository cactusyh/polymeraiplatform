"""Typed API schemas for polymer scientific data management."""
import uuid
from datetime import datetime
from typing import Any, Generic, Literal, TypeVar
from pydantic import BaseModel, ConfigDict, Field, field_validator
Architecture=Literal["homopolymer","random_copolymer","alternating_copolymer","block_copolymer","graft_copolymer","branched","crosslinked","unknown"]
RepresentationType=Literal["psmiles","smiles","repeat_unit_smiles","other"]; ProvenanceType=Literal["experiment","simulation","prediction","literature","unknown"]; SourceType=Literal["paper","dataset","experiment","simulation","model","manual","unknown"]
class ORMModel(BaseModel): model_config=ConfigDict(from_attributes=True)
def _text(value:str,label:str)->str:
    value=value.strip()
    if not value: raise ValueError(f"{label} must not be empty")
    return value
class PolymerStructureCreate(BaseModel):
    representation_type:RepresentationType; representation:str=Field(max_length=4096); is_canonical:bool=False; source:str|None=Field(default=None,max_length=255)
    @field_validator("representation")
    @classmethod
    def validate_representation(cls,v:str)->str:return _text(v,"structure representation")
class PolymerStructureRead(ORMModel): id:uuid.UUID; polymer_id:uuid.UUID; representation_type:RepresentationType; representation:str; is_canonical:bool; source:str|None; validation_status:Literal["not_validated","valid","partially_valid","invalid","unsupported"]; validation_message:str|None; normalized_representation:str|None; connection_point_count:int|None; normalization_version:str|None; rdkit_version:str|None; validated_at:datetime|None; derived_properties:dict[str,Any]|None; created_at:datetime
class PolymerCreate(BaseModel):
    name:str=Field(max_length=255); canonical_name:str|None=Field(default=None,max_length=255); description:str|None=None; polymer_class:str|None=Field(default=None,max_length=100); architecture:Architecture="unknown"; number_average_molecular_weight:float|None=Field(default=None,gt=0); weight_average_molecular_weight:float|None=Field(default=None,gt=0); dispersity:float|None=Field(default=None,gt=0); degree_of_polymerization:float|None=Field(default=None,gt=0); composition_metadata:dict[str,Any]|None=None; structures:list[PolymerStructureCreate]=Field(default_factory=list)
    @field_validator("name")
    @classmethod
    def validate_name(cls,v:str)->str:return _text(v,"polymer name")
    @field_validator("canonical_name")
    @classmethod
    def validate_canonical(cls,v:str|None)->str|None:return None if v is None else _text(v,"canonical polymer name")
class PolymerUpdate(BaseModel):
    name:str|None=Field(default=None,max_length=255); canonical_name:str|None=Field(default=None,max_length=255); description:str|None=None; polymer_class:str|None=Field(default=None,max_length=100); architecture:Architecture|None=None; number_average_molecular_weight:float|None=Field(default=None,gt=0); weight_average_molecular_weight:float|None=Field(default=None,gt=0); dispersity:float|None=Field(default=None,gt=0); degree_of_polymerization:float|None=Field(default=None,gt=0); composition_metadata:dict[str,Any]|None=None
    @field_validator("name","canonical_name")
    @classmethod
    def validate_optional_names(cls,v:str|None)->str|None:return None if v is None else _text(v,"polymer name")
class PropertyDefinitionCreate(BaseModel): key:str=Field(pattern=r"^[a-z][a-z0-9_]*$",max_length=100); name:str=Field(min_length=1,max_length=255); symbol:str|None=None; description:str|None=None; canonical_unit:str=Field(max_length=100); category:str|None=None
class PropertyDefinitionRead(ORMModel): id:uuid.UUID; key:str; name:str; symbol:str|None; description:str|None; canonical_unit:str; category:str|None; created_at:datetime
class ProvenanceCreate(BaseModel): source_type:SourceType="unknown"; title:str|None=None; authors:str|None=None; year:int|None=Field(default=None,ge=1,le=9999); doi:str|None=None; url:str|None=None; dataset_name:str|None=None; notes:str|None=None; metadata:dict[str,Any]|None=None
class ProvenanceRead(ORMModel): id:uuid.UUID; source_type:SourceType; title:str|None; authors:str|None; year:int|None; doi:str|None; url:str|None; dataset_name:str|None; notes:str|None; metadata:dict[str,Any]|None=Field(validation_alias="metadata_"); created_at:datetime
class PropertyRecordCreate(BaseModel):
    property_definition_id:uuid.UUID; value:float; unit:str=Field(max_length=100); uncertainty:float|None=Field(default=None,ge=0); uncertainty_type:str|None=None; provenance_type:ProvenanceType="unknown"; method:str|None=None; temperature:float|None=None; temperature_unit:str|None=None; pressure:float|None=None; pressure_unit:str|None=None; conditions:dict[str,Any]|None=None; provenance_id:uuid.UUID|None=None
    @field_validator("unit")
    @classmethod
    def validate_unit(cls,v:str)->str:return _text(v,"property unit")
class PropertyRecordRead(ORMModel): id:uuid.UUID; polymer_id:uuid.UUID; property:PropertyDefinitionRead=Field(validation_alias="property_definition"); value:float; unit:str; uncertainty:float|None; uncertainty_type:str|None; provenance_type:ProvenanceType; method:str|None; temperature:float|None; temperature_unit:str|None; pressure:float|None; pressure_unit:str|None; conditions:dict[str,Any]|None; provenance:ProvenanceRead|None; created_at:datetime; updated_at:datetime
class PolymerRead(ORMModel): id:uuid.UUID; name:str; canonical_name:str; description:str|None; polymer_class:str|None; architecture:Architecture; number_average_molecular_weight:float|None; weight_average_molecular_weight:float|None; dispersity:float|None; degree_of_polymerization:float|None; composition_metadata:dict[str,Any]|None; structures:list[PolymerStructureRead]; property_records:list[PropertyRecordRead]; created_at:datetime; updated_at:datetime
class PolymerListItem(ORMModel): id:uuid.UUID; name:str; canonical_name:str; polymer_class:str|None; architecture:Architecture; structure_count:int; property_record_count:int; created_at:datetime; updated_at:datetime
T=TypeVar("T")
class Page(BaseModel,Generic[T]): items:list[T]; total:int; limit:int; offset:int
