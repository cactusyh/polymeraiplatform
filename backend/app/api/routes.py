"""Versioned application API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models import Polymer, PolymerStructure, PropertyDefinition, PropertyRecord, Provenance
from backend.app.schemas.polymer import PolymerCreate, PolymerRead, PropertyDefinitionCreate, PropertyDefinitionRead, PropertyRecordCreate, PropertyRecordRead

router = APIRouter(prefix="/api/v1", tags=["platform"])


@router.get("/info")
def platform_info() -> dict[str, str]:
    """Return non-sensitive metadata about this platform instance."""
    return {"name": settings.app_name, "version": settings.app_version, "status": settings.app_env}


@router.post("/polymers", response_model=PolymerRead, status_code=status.HTTP_201_CREATED, tags=["polymers"])
def create_polymer(payload: PolymerCreate, db: Session = Depends(get_db)) -> Polymer:
    """Create a polymer identity, optionally with supplied structure representations."""
    canonical_name = payload.canonical_name.strip() if payload.canonical_name else payload.name
    polymer = Polymer(**payload.model_dump(exclude={"structures", "canonical_name"}), canonical_name=canonical_name)
    polymer.structures = [PolymerStructure(**structure.model_dump()) for structure in payload.structures]
    db.add(polymer)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="canonical polymer name already exists") from error
    return _get_polymer_or_404(db, polymer.id)


@router.get("/polymers/{polymer_id}", response_model=PolymerRead, tags=["polymers"])
def get_polymer(polymer_id: uuid.UUID, db: Session = Depends(get_db)) -> Polymer:
    """Retrieve a polymer with structures and provenance-explicit property records."""
    return _get_polymer_or_404(db, polymer_id)


@router.post("/property-definitions", response_model=PropertyDefinitionRead, status_code=status.HTTP_201_CREATED, tags=["properties"])
def create_property_definition(payload: PropertyDefinitionCreate, db: Session = Depends(get_db)) -> PropertyDefinition:
    """Create an extensible, database-backed scientific property definition."""
    definition = PropertyDefinition(**payload.model_dump())
    db.add(definition)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="property key already exists") from error
    db.refresh(definition)
    return definition


@router.get("/property-definitions/{property_definition_id}", response_model=PropertyDefinitionRead, tags=["properties"])
def get_property_definition(property_definition_id: uuid.UUID, db: Session = Depends(get_db)) -> PropertyDefinition:
    """Retrieve one property definition."""
    definition = db.get(PropertyDefinition, property_definition_id)
    if definition is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="property definition not found")
    return definition


@router.post("/polymers/{polymer_id}/properties", response_model=PropertyRecordRead, status_code=status.HTTP_201_CREATED, tags=["properties"])
def create_property_record(polymer_id: uuid.UUID, payload: PropertyRecordCreate, db: Session = Depends(get_db)) -> PropertyRecord:
    """Attach a particular scientific property value to a polymer."""
    _get_polymer_or_404(db, polymer_id)
    if db.get(PropertyDefinition, payload.property_definition_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="property definition not found")
    if payload.provenance_id is not None and db.get(Provenance, payload.provenance_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="provenance not found")
    record = PropertyRecord(polymer_id=polymer_id, **payload.model_dump())
    db.add(record)
    db.commit()
    return _get_property_record(db, record.id)


def _get_polymer_or_404(db: Session, polymer_id: uuid.UUID) -> Polymer:
    statement = select(Polymer).where(Polymer.id == polymer_id).options(
        selectinload(Polymer.structures),
        selectinload(Polymer.property_records).selectinload(PropertyRecord.property_definition),
        selectinload(Polymer.property_records).selectinload(PropertyRecord.provenance),
    )
    polymer = db.scalar(statement)
    if polymer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="polymer not found")
    return polymer


def _get_property_record(db: Session, record_id: uuid.UUID) -> PropertyRecord:
    statement = select(PropertyRecord).where(PropertyRecord.id == record_id).options(
        selectinload(PropertyRecord.property_definition), selectinload(PropertyRecord.provenance)
    )
    record = db.scalar(statement)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="property record not found")
    return record
