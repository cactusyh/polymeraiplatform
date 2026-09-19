"""Request and response schemas for the scientific data model."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Architecture = Literal["homopolymer", "random_copolymer", "alternating_copolymer", "block_copolymer", "graft_copolymer", "branched", "crosslinked", "unknown"]
RepresentationType = Literal["psmiles", "smiles", "repeat_unit_smiles", "other"]
ProvenanceType = Literal["experiment", "simulation", "prediction", "literature", "unknown"]
SourceType = Literal["paper", "dataset", "experiment", "simulation", "model", "manual", "unknown"]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PolymerStructureCreate(BaseModel):
    representation_type: RepresentationType
    representation: str = Field(max_length=4096)
    is_canonical: bool = False
    source: str | None = Field(default=None, max_length=255)

    @field_validator("representation")
    @classmethod
    def structure_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("structure representation must not be empty")
        return value


class PolymerStructureRead(ORMModel):
    id: uuid.UUID
    polymer_id: uuid.UUID
    representation_type: RepresentationType
    representation: str
    is_canonical: bool
    source: str | None
    created_at: datetime


class PolymerCreate(BaseModel):
    name: str = Field(max_length=255)
    canonical_name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    polymer_class: str | None = Field(default=None, max_length=100)
    architecture: Architecture = "unknown"
    number_average_molecular_weight: float | None = Field(default=None, gt=0, description="Mn in g/mol; MVP identity-level field")
    weight_average_molecular_weight: float | None = Field(default=None, gt=0, description="Mw in g/mol; MVP identity-level field")
    dispersity: float | None = Field(default=None, gt=0)
    degree_of_polymerization: float | None = Field(default=None, gt=0)
    composition_metadata: dict[str, Any] | None = None
    structures: list[PolymerStructureCreate] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("polymer name must not be empty")
        return value


class PropertyDefinitionCreate(BaseModel):
    key: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=100)
    name: str = Field(min_length=1, max_length=255)
    symbol: str | None = Field(default=None, max_length=50)
    description: str | None = None
    canonical_unit: str = Field(max_length=100)
    category: str | None = Field(default=None, max_length=100)

    @field_validator("canonical_unit")
    @classmethod
    def canonical_unit_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("canonical unit must not be empty")
        return value


class PropertyDefinitionRead(ORMModel):
    id: uuid.UUID
    key: str
    name: str
    symbol: str | None
    description: str | None
    canonical_unit: str
    category: str | None
    created_at: datetime


class ProvenanceCreate(BaseModel):
    source_type: SourceType = "unknown"
    title: str | None = Field(default=None, max_length=500)
    authors: str | None = None
    year: int | None = Field(default=None, ge=1, le=9999)
    doi: str | None = Field(default=None, max_length=255)
    url: str | None = Field(default=None, max_length=2048)
    dataset_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    metadata: dict[str, Any] | None = None


class ProvenanceRead(ORMModel):
    id: uuid.UUID
    source_type: SourceType
    title: str | None
    authors: str | None
    year: int | None
    doi: str | None
    url: str | None
    dataset_name: str | None
    notes: str | None
    metadata: dict[str, Any] | None = Field(validation_alias="metadata_")
    created_at: datetime


class PropertyRecordCreate(BaseModel):
    property_definition_id: uuid.UUID
    value: float
    unit: str = Field(max_length=100)
    uncertainty: float | None = None
    uncertainty_type: str | None = Field(default=None, max_length=100)
    provenance_type: ProvenanceType = "unknown"
    method: str | None = Field(default=None, max_length=255)
    temperature: float | None = None
    temperature_unit: str | None = Field(default=None, max_length=50)
    pressure: float | None = None
    pressure_unit: str | None = Field(default=None, max_length=50)
    conditions: dict[str, Any] | None = None
    provenance_id: uuid.UUID | None = None

    @field_validator("unit")
    @classmethod
    def unit_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("property unit must not be empty")
        return value


class PropertyRecordRead(ORMModel):
    id: uuid.UUID
    polymer_id: uuid.UUID
    property: PropertyDefinitionRead = Field(validation_alias="property_definition")
    value: float
    unit: str
    uncertainty: float | None
    uncertainty_type: str | None
    provenance_type: ProvenanceType
    method: str | None
    temperature: float | None
    temperature_unit: str | None
    pressure: float | None
    pressure_unit: str | None
    conditions: dict[str, Any] | None
    provenance: ProvenanceRead | None
    created_at: datetime
    updated_at: datetime


class PolymerRead(ORMModel):
    id: uuid.UUID
    name: str
    canonical_name: str
    description: str | None
    polymer_class: str | None
    architecture: Architecture
    number_average_molecular_weight: float | None
    weight_average_molecular_weight: float | None
    dispersity: float | None
    degree_of_polymerization: float | None
    composition_metadata: dict[str, Any] | None
    structures: list[PolymerStructureRead]
    property_records: list[PropertyRecordRead]
    created_at: datetime
    updated_at: datetime
