"""Typed public request and response schemas for chemistry endpoints."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ValidationStatus = Literal["not_validated", "valid", "partially_valid", "invalid", "unsupported"]


class FingerprintMetadata(BaseModel):
    algorithm: Literal["Morgan"]
    radius: Literal[2]
    n_bits: Literal[2048]
    attachment_handling: Literal["wildcards_retained"]


class ChemistryValidationRequest(BaseModel):
    representation_type: str = Field(min_length=1, max_length=50)
    representation: str = Field(min_length=1, max_length=4096)


class ChemistryValidationResponse(BaseModel):
    status: ValidationStatus
    validation_message: str | None
    warnings: list[str]
    normalized_representation: str | None
    connection_point_count: int | None
    derived_properties: dict[str, float | int] | None
    rdkit_version: str | None
    normalization_version: str | None
    validated_at: datetime | None
    fingerprint_config: FingerprintMetadata


class SimilaritySearchRequest(ChemistryValidationRequest):
    limit: int = Field(default=20, ge=1, le=100)
    minimum_similarity: float = Field(default=0.3, ge=0, le=1)


class SimilaritySearchResult(BaseModel):
    polymer_id: str
    polymer_name: str
    structure_id: str
    raw_representation: str
    normalized_representation: str
    similarity: float
    fingerprint_config: FingerprintMetadata


class SimilaritySearchResponse(BaseModel):
    items: list[SimilaritySearchResult]
    fingerprint_config: FingerprintMetadata
