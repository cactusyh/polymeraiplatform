"""Versioned API for scientific polymer data management."""
import uuid
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models import Polymer, PolymerStructure, PropertyDefinition, PropertyRecord, Provenance
from backend.app.schemas.polymer import Page, PolymerCreate, PolymerListItem, PolymerRead, PolymerStructureCreate, PolymerStructureRead, PolymerUpdate, PropertyDefinitionCreate, PropertyDefinitionRead, PropertyRecordCreate, PropertyRecordRead, ProvenanceCreate, ProvenanceRead
router=APIRouter(prefix="/api/v1",tags=["platform"])
MAX_LIMIT=100
def _page(limit:int=Query(20,ge=1,le=MAX_LIMIT),offset:int=Query(0,ge=0))->tuple[int,int]: return limit,offset
@router.get("/info")
def platform_info()->dict[str,str]: return {"name":settings.app_name,"version":settings.app_version,"status":settings.app_env}
@router.get("/polymers",response_model=Page[PolymerListItem],tags=["polymers"])
def list_polymers(q:str|None=None,polymer_class:str|None=None,architecture:str|None=None,property_key:str|None=None,provenance_type:str|None=None,sort:Literal["name","created_at","updated_at"]="name",order:Literal["asc","desc"]="asc",page:tuple[int,int]=Depends(_page),db:Session=Depends(get_db)):
    limit,offset=page; stmt=select(Polymer); filters=[]
    if q:
        pattern=f"%{q.strip()}%"; filters.append(or_(Polymer.name.ilike(pattern),Polymer.canonical_name.ilike(pattern)))
    if polymer_class: filters.append(Polymer.polymer_class==polymer_class)
    if architecture:
        if architecture not in {"homopolymer","random_copolymer","alternating_copolymer","block_copolymer","graft_copolymer","branched","crosslinked","unknown"}: raise HTTPException(422,"invalid architecture")
        filters.append(Polymer.architecture==architecture)
    if property_key: stmt=stmt.join(PropertyRecord).join(PropertyDefinition); filters.append(PropertyDefinition.key==property_key)
    if provenance_type:
        if provenance_type not in {"experiment","simulation","prediction","literature","unknown"}: raise HTTPException(422,"invalid provenance type")
        if not property_key: stmt=stmt.join(PropertyRecord)
        filters.append(PropertyRecord.provenance_type==provenance_type)
    stmt=stmt.where(*filters).distinct(); total=db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    column=getattr(Polymer,sort); stmt=stmt.order_by(column.desc() if order=="desc" else column.asc(),Polymer.id.asc()).limit(limit).offset(offset)
    polymers=db.scalars(stmt).all()
    items=[PolymerListItem(id=p.id,name=p.name,canonical_name=p.canonical_name,polymer_class=p.polymer_class,architecture=p.architecture,structure_count=db.scalar(select(func.count()).select_from(PolymerStructure).where(PolymerStructure.polymer_id==p.id)) or 0,property_record_count=db.scalar(select(func.count()).select_from(PropertyRecord).where(PropertyRecord.polymer_id==p.id)) or 0,created_at=p.created_at,updated_at=p.updated_at) for p in polymers]
    return Page(items=items,total=total,limit=limit,offset=offset)
@router.post("/polymers",response_model=PolymerRead,status_code=201,tags=["polymers"])
def create_polymer(payload:PolymerCreate,db:Session=Depends(get_db)):
    polymer=Polymer(**payload.model_dump(exclude={"structures","canonical_name"}),canonical_name=payload.canonical_name or payload.name); polymer.structures=[PolymerStructure(**x.model_dump()) for x in payload.structures]; db.add(polymer); _commit_or_409(db,"canonical polymer name already exists"); return _polymer(db,polymer.id)
@router.get("/polymers/{polymer_id}",response_model=PolymerRead,tags=["polymers"])
def get_polymer(polymer_id:uuid.UUID,db:Session=Depends(get_db)): return _polymer(db,polymer_id)
@router.patch("/polymers/{polymer_id}",response_model=PolymerRead,tags=["polymers"])
def update_polymer(polymer_id:uuid.UUID,payload:PolymerUpdate,db:Session=Depends(get_db)):
    values=payload.model_dump(exclude_unset=True)
    if not values: raise HTTPException(422,"patch body must contain at least one field")
    polymer=_polymer(db,polymer_id)
    for key,value in values.items(): setattr(polymer,key,value)
    _commit_or_409(db,"canonical polymer name already exists"); return _polymer(db,polymer_id)
@router.post("/polymers/{polymer_id}/structures",response_model=PolymerStructureRead,status_code=201,tags=["polymers"])
def add_structure(polymer_id:uuid.UUID,payload:PolymerStructureCreate,db:Session=Depends(get_db)):
    _polymer(db,polymer_id); structure=PolymerStructure(polymer_id=polymer_id,**payload.model_dump()); db.add(structure); db.commit(); db.refresh(structure); return structure
@router.get("/polymers/{polymer_id}/properties",response_model=Page[PropertyRecordRead],tags=["properties"])
def list_property_records(polymer_id:uuid.UUID,property_key:str|None=None,provenance_type:str|None=None,page:tuple[int,int]=Depends(_page),db:Session=Depends(get_db)):
    _polymer(db,polymer_id); limit,offset=page; stmt=select(PropertyRecord).where(PropertyRecord.polymer_id==polymer_id).options(selectinload(PropertyRecord.property_definition),selectinload(PropertyRecord.provenance))
    if property_key: stmt=stmt.join(PropertyDefinition).where(PropertyDefinition.key==property_key)
    if provenance_type: stmt=stmt.where(PropertyRecord.provenance_type==provenance_type)
    total=db.scalar(select(func.count()).select_from(stmt.subquery())) or 0; items=db.scalars(stmt.order_by(PropertyRecord.created_at.desc()).limit(limit).offset(offset)).all(); return Page(items=items,total=total,limit=limit,offset=offset)
@router.post("/polymers/{polymer_id}/properties",response_model=PropertyRecordRead,status_code=201,tags=["properties"])
def create_property_record(polymer_id:uuid.UUID,payload:PropertyRecordCreate,db:Session=Depends(get_db)):
    _polymer(db,polymer_id)
    if not db.get(PropertyDefinition,payload.property_definition_id): raise HTTPException(404,"property definition not found")
    if payload.provenance_id and not db.get(Provenance,payload.provenance_id): raise HTTPException(404,"provenance not found")
    record=PropertyRecord(polymer_id=polymer_id,**payload.model_dump()); db.add(record); db.commit(); return _record(db,record.id)
@router.get("/property-definitions",response_model=Page[PropertyDefinitionRead],tags=["properties"])
def list_property_definitions(q:str|None=None,category:str|None=None,page:tuple[int,int]=Depends(_page),db:Session=Depends(get_db)):
    limit,offset=page; stmt=select(PropertyDefinition)
    if q: stmt=stmt.where(or_(PropertyDefinition.key.ilike(f"%{q}%"),PropertyDefinition.name.ilike(f"%{q}%")))
    if category: stmt=stmt.where(PropertyDefinition.category==category)
    total=db.scalar(select(func.count()).select_from(stmt.subquery())) or 0; return Page(items=db.scalars(stmt.order_by(PropertyDefinition.key).limit(limit).offset(offset)).all(),total=total,limit=limit,offset=offset)
@router.post("/property-definitions",response_model=PropertyDefinitionRead,status_code=201,tags=["properties"])
def create_property_definition(payload:PropertyDefinitionCreate,db:Session=Depends(get_db)):
    item=PropertyDefinition(**payload.model_dump()); db.add(item); _commit_or_409(db,"property key already exists"); db.refresh(item); return item
@router.get("/property-definitions/{item_id}",response_model=PropertyDefinitionRead,tags=["properties"])
def get_property_definition(item_id:uuid.UUID,db:Session=Depends(get_db)):
    item=db.get(PropertyDefinition,item_id)
    if not item: raise HTTPException(404,"property definition not found")
    return item
@router.get("/provenance",response_model=Page[ProvenanceRead],tags=["provenance"])
def list_provenance(page:tuple[int,int]=Depends(_page),db:Session=Depends(get_db)):
    limit,offset=page; total=db.scalar(select(func.count()).select_from(Provenance)) or 0; return Page(items=db.scalars(select(Provenance).order_by(Provenance.created_at.desc()).limit(limit).offset(offset)).all(),total=total,limit=limit,offset=offset)
@router.post("/provenance",response_model=ProvenanceRead,status_code=201,tags=["provenance"])
def create_provenance(payload:ProvenanceCreate,db:Session=Depends(get_db)):
    item=Provenance(**payload.model_dump(by_alias=False,exclude={"metadata"}),metadata_=payload.metadata); db.add(item); db.commit(); db.refresh(item); return item
@router.get("/provenance/{item_id}",response_model=ProvenanceRead,tags=["provenance"])
def get_provenance(item_id:uuid.UUID,db:Session=Depends(get_db)):
    item=db.get(Provenance,item_id)
    if not item: raise HTTPException(404,"provenance not found")
    return item
def _commit_or_409(db:Session,detail:str)->None:
    try: db.commit()
    except IntegrityError as error: db.rollback(); raise HTTPException(409,detail) from error
def _polymer(db:Session,item_id:uuid.UUID)->Polymer:
    item=db.scalar(select(Polymer).where(Polymer.id==item_id).options(selectinload(Polymer.structures),selectinload(Polymer.property_records).selectinload(PropertyRecord.property_definition),selectinload(Polymer.property_records).selectinload(PropertyRecord.provenance)))
    if not item: raise HTTPException(404,"polymer not found")
    return item
def _record(db:Session,item_id:uuid.UUID)->PropertyRecord:
    item=db.scalar(select(PropertyRecord).where(PropertyRecord.id==item_id).options(selectinload(PropertyRecord.property_definition),selectinload(PropertyRecord.provenance)))
    if not item: raise HTTPException(404,"property record not found")
    return item
