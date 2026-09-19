"""Dedicated chemistry API router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.chemistry.service import ChemistryProcessingError, FINGERPRINT_CONFIG, process, similarity
from backend.app.db.session import get_db
from backend.app.models import Polymer, PolymerStructure
from backend.app.schemas.chemistry import (
    ChemistryValidationRequest,
    ChemistryValidationResponse,
    SimilaritySearchRequest,
    SimilaritySearchResponse,
)

router = APIRouter(prefix="/api/v1/chemistry", tags=["chemistry"])


@router.post("/validate", response_model=ChemistryValidationResponse)
def validate(payload: ChemistryValidationRequest) -> ChemistryValidationResponse:
    result = process(payload.representation_type, payload.representation)
    return ChemistryValidationResponse(**result.__dict__, fingerprint_config=FINGERPRINT_CONFIG)


@router.post("/similarity-search", response_model=SimilaritySearchResponse)
def search(payload: SimilaritySearchRequest, db: Session = Depends(get_db)) -> SimilaritySearchResponse:
    query = process(payload.representation_type, payload.representation)
    if not query.normalized_representation:
        raise HTTPException(422, "Query structure could not produce a repeat-unit fingerprint.")
    try:
        similarity(query.normalized_representation, query.normalized_representation)
    except ChemistryProcessingError as error:
        raise HTTPException(422, "Query structure could not produce a repeat-unit fingerprint.") from error

    items = []
    for structure, polymer in db.execute(select(PolymerStructure, Polymer).join(Polymer)).all():
        if structure.validation_status not in {"valid", "partially_valid"} or not structure.normalized_representation:
            continue
        try:
            score = similarity(query.normalized_representation, structure.normalized_representation)
        except ChemistryProcessingError:
            continue
        if score >= payload.minimum_similarity:
            items.append({
                "polymer_id": str(polymer.id),
                "polymer_name": polymer.name,
                "structure_id": str(structure.id),
                "raw_representation": structure.representation,
                "normalized_representation": structure.normalized_representation,
                "similarity": score,
                "fingerprint_config": FINGERPRINT_CONFIG,
            })
    items.sort(key=lambda item: (-item["similarity"], item["polymer_name"], item["structure_id"]))
    return SimilaritySearchResponse(items=items[:payload.limit], fingerprint_config=FINGERPRINT_CONFIG)
