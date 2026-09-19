"""Typed chemistry processing; raw source text is never changed."""
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from rdkit import Chem, rdBase
from rdkit.Chem import Descriptors,rdFingerprintGenerator,DataStructs
NORMALIZATION_VERSION="phase4-v1"; FP={"algorithm":"Morgan","radius":2,"n_bits":2048,"attachment_handling":"wildcards_retained"}
@dataclass
class Result:
 status:str; validation_message:str|None; normalized_representation:str|None; connection_point_count:int|None; warnings:list[str]; derived_properties:dict|None; rdkit_version:str=rdBase.rdkitVersion; normalization_version:str=NORMALIZATION_VERSION; validated_at:datetime|None=None
def process(representation_type:str,representation:str)->Result:
 if representation_type not in {"smiles","psmiles","repeat_unit_smiles"}: return Result("unsupported","Representation type is stored but not supported by the chemistry engine.",None,None,[],None)
 mol=Chem.MolFromSmiles(representation)
 if not mol:return Result("invalid","Unable to parse the supplied structure representation.",None,None,[],None)
 points=sum(1 for a in mol.GetAtoms() if a.GetAtomicNum()==0)
 warnings=[]; status="valid"
 if representation_type=="psmiles" and points!=2: status="partially_valid";warnings.append(f"Connection-point count is {points}; Phase 4 does not require exactly two.")
 props={"heavy_atom_count":mol.GetNumHeavyAtoms(),"heteroatom_count":sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() not in (0,1,6)),"ring_count":mol.GetRingInfo().NumRings(),"aromatic_ring_count":sum(1 for r in mol.GetRingInfo().AtomRings() if all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in r)),"rotatable_bond_count":Descriptors.NumRotatableBonds(mol),"fraction_csp3":Descriptors.FractionCSP3(mol)}
 return Result(status,None,Chem.MolToSmiles(mol,canonical=True),points,warnings,props,validated_at=datetime.now(timezone.utc))
def fingerprint(normalized:str):
 mol=Chem.MolFromSmiles(normalized)
 if not mol: return None
 return rdFingerprintGenerator.GetMorganGenerator(radius=2,fpSize=2048).GetFingerprint(mol)
def similarity(left:str,right:str)->float:return DataStructs.TanimotoSimilarity(fingerprint(left),fingerprint(right))
