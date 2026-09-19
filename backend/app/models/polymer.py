"""Scientific polymer identity, structure, property, and provenance models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

ARCHITECTURES = ("homopolymer", "random_copolymer", "alternating_copolymer", "block_copolymer", "graft_copolymer", "branched", "crosslinked", "unknown")
REPRESENTATION_TYPES = ("psmiles", "smiles", "repeat_unit_smiles", "other")
PROPERTY_PROVENANCE_TYPES = ("experiment", "simulation", "prediction", "literature", "unknown")
SOURCE_TYPES = ("paper", "dataset", "experiment", "simulation", "model", "manual", "unknown")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Polymer(TimestampMixin, Base):
    __tablename__ = "polymers"
    __table_args__ = (
        CheckConstraint(f"architecture IN {ARCHITECTURES!r}", name="ck_polymer_architecture"),
        CheckConstraint("number_average_molecular_weight IS NULL OR number_average_molecular_weight > 0", name="ck_polymer_mn_positive"),
        CheckConstraint("weight_average_molecular_weight IS NULL OR weight_average_molecular_weight > 0", name="ck_polymer_mw_positive"),
        CheckConstraint("dispersity IS NULL OR dispersity > 0", name="ck_polymer_dispersity_positive"),
        CheckConstraint("degree_of_polymerization IS NULL OR degree_of_polymerization > 0", name="ck_polymer_dp_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    polymer_class: Mapped[str | None] = mapped_column(String(100), nullable=True)
    architecture: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    # MVP convenience only: these attributes logically belong to a future MaterialSample.
    number_average_molecular_weight: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Mn, g/mol; MVP identity-level convenience")
    weight_average_molecular_weight: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Mw, g/mol; MVP identity-level convenience")
    dispersity: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Dimensionless; MVP identity-level convenience")
    degree_of_polymerization: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Dimensionless; MVP identity-level convenience")
    composition_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    structures: Mapped[list["PolymerStructure"]] = relationship(back_populates="polymer", cascade="all, delete-orphan")
    property_records: Mapped[list["PropertyRecord"]] = relationship(back_populates="polymer", cascade="all, delete-orphan")


class PolymerStructure(TimestampMixin, Base):
    __tablename__ = "polymer_structures"
    __table_args__ = (CheckConstraint(f"representation_type IN {REPRESENTATION_TYPES!r}", name="ck_structure_representation_type"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    polymer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("polymers.id", ondelete="CASCADE"), nullable=False, index=True)
    representation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    representation: Mapped[str] = mapped_column(String(4096), nullable=False)
    is_canonical: Mapped[bool] = mapped_column(nullable=False, default=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    polymer: Mapped[Polymer] = relationship(back_populates="structures")


class PropertyDefinition(TimestampMixin, Base):
    __tablename__ = "property_definitions"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    canonical_unit: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    property_records: Mapped[list["PropertyRecord"]] = relationship(back_populates="property_definition", passive_deletes="all")


class Provenance(TimestampMixin, Base):
    __tablename__ = "provenance"
    __table_args__ = (CheckConstraint(f"source_type IN {SOURCE_TYPES!r}", name="ck_provenance_source_type"),)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    dataset_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)
    property_records: Mapped[list["PropertyRecord"]] = relationship(back_populates="provenance", passive_deletes="all")


class PropertyRecord(TimestampMixin, Base):
    __tablename__ = "property_records"
    __table_args__ = (
        CheckConstraint(f"provenance_type IN {PROPERTY_PROVENANCE_TYPES!r}", name="ck_property_record_provenance_type"),
        CheckConstraint("uncertainty IS NULL OR uncertainty >= 0", name="ck_property_record_uncertainty_nonnegative"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    polymer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("polymers.id", ondelete="CASCADE"), nullable=False, index=True)
    property_definition_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("property_definitions.id", name="fk_property_records_property_definition_id_property_definitions", ondelete="RESTRICT"), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(100), nullable=False)
    uncertainty: Mapped[float | None] = mapped_column(Float, nullable=True)
    uncertainty_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provenance_type: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    method: Mapped[str | None] = mapped_column(String(255), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    conditions: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    provenance_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("provenance.id", name="fk_property_records_provenance_id_provenance", ondelete="RESTRICT"), nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    polymer: Mapped[Polymer] = relationship(back_populates="property_records")
    property_definition: Mapped[PropertyDefinition] = relationship(back_populates="property_records")
    provenance: Mapped[Provenance | None] = relationship(back_populates="property_records")
