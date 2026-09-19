"""Explicit repeatable Phase 4 chemistry backfill."""
from backend.app.chemistry.service import process
from backend.app.db.session import SessionLocal
from backend.app.models import PolymerStructure
def main():
 db=SessionLocal();counts={}
 for s in db.query(PolymerStructure):
  r=process(s.representation_type,s.representation);s.validation_status=r.status;s.validation_message="; ".join(r.warnings) if r.warnings else r.validation_message;s.normalized_representation=r.normalized_representation;s.connection_point_count=r.connection_point_count;s.normalization_version=r.normalization_version;s.rdkit_version=r.rdkit_version;s.validated_at=r.validated_at;s.derived_properties=r.derived_properties;counts[r.status]=counts.get(r.status,0)+1
 db.commit();print(counts)
if __name__=="__main__":main()
