"""Dedicated chemistry API router."""
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.chemistry.service import FP,process,fingerprint,similarity
from backend.app.db.session import get_db
from backend.app.models import Polymer,PolymerStructure
router=APIRouter(prefix="/api/v1/chemistry",tags=["chemistry"])
class Validate(BaseModel): representation_type:str;representation:str=Field(min_length=1,max_length=4096)
class Search(Validate): limit:int=Field(20,ge=1,le=100);minimum_similarity:float=Field(.3,ge=0,le=1)
@router.post("/validate")
def validate(payload:Validate):
 r=process(payload.representation_type,payload.representation);return {**r.__dict__,"fingerprint":FP}
@router.post("/similarity-search")
def search(payload:Search,db:Session=Depends(get_db)):
 q=process(payload.representation_type,payload.representation)
 if not q.normalized_representation: raise HTTPException(422,"Query structure could not produce a repeat-unit fingerprint.")
 out=[]
 for s,p in db.execute(select(PolymerStructure,Polymer).join(Polymer)).all():
  if s.validation_status not in {"valid","partially_valid"} or not s.normalized_representation: continue
  score=similarity(q.normalized_representation,s.normalized_representation)
  if score>=payload.minimum_similarity:out.append({"polymer_id":str(p.id),"polymer_name":p.name,"structure_id":str(s.id),"raw_representation":s.representation,"normalized_representation":s.normalized_representation,"similarity":score,"fingerprint":FP})
 return {"items":sorted(out,key=lambda x:(-x["similarity"],x["polymer_name"],x["structure_id"]))[:payload.limit],"fingerprint":FP}
