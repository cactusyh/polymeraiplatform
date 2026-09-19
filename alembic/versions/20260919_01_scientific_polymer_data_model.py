"""add scientific polymer data model

Revision ID: 20260919_01
Revises:
Create Date: 2026-09-19
"""

from alembic import op
import sqlalchemy as sa


revision = "20260919_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid_type = sa.Uuid()
    op.create_table(
        "polymers",
        sa.Column("id", uuid_type, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("canonical_name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("polymer_class", sa.String(100)),
        sa.Column("architecture", sa.String(50), nullable=False),
        sa.Column("number_average_molecular_weight", sa.Float(), comment="Mn, g/mol; MVP identity-level convenience"),
        sa.Column("weight_average_molecular_weight", sa.Float(), comment="Mw, g/mol; MVP identity-level convenience"),
        sa.Column("dispersity", sa.Float(), comment="Dimensionless; MVP identity-level convenience"),
        sa.Column("degree_of_polymerization", sa.Float(), comment="Dimensionless; MVP identity-level convenience"),
        sa.Column("composition_metadata", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("architecture IN ('homopolymer', 'random_copolymer', 'alternating_copolymer', 'block_copolymer', 'graft_copolymer', 'branched', 'crosslinked', 'unknown')", name="ck_polymer_architecture"),
    )
    op.create_table(
        "property_definitions",
        sa.Column("id", uuid_type, primary_key=True), sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False), sa.Column("symbol", sa.String(50)), sa.Column("description", sa.Text()),
        sa.Column("canonical_unit", sa.String(100), nullable=False), sa.Column("category", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_table(
        "provenance",
        sa.Column("id", uuid_type, primary_key=True), sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500)), sa.Column("authors", sa.Text()), sa.Column("year", sa.Integer()), sa.Column("doi", sa.String(255)),
        sa.Column("url", sa.String(2048)), sa.Column("dataset_name", sa.String(255)), sa.Column("notes", sa.Text()), sa.Column("metadata", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("source_type IN ('paper', 'dataset', 'experiment', 'simulation', 'model', 'manual', 'unknown')", name="ck_provenance_source_type"),
    )
    op.create_table(
        "polymer_structures",
        sa.Column("id", uuid_type, primary_key=True), sa.Column("polymer_id", uuid_type, sa.ForeignKey("polymers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("representation_type", sa.String(50), nullable=False), sa.Column("representation", sa.String(4096), nullable=False), sa.Column("is_canonical", sa.Boolean(), nullable=False), sa.Column("source", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("representation_type IN ('psmiles', 'smiles', 'repeat_unit_smiles', 'other')", name="ck_structure_representation_type"),
    )
    op.create_index("ix_polymer_structures_polymer_id", "polymer_structures", ["polymer_id"])
    op.create_table(
        "property_records",
        sa.Column("id", uuid_type, primary_key=True), sa.Column("polymer_id", uuid_type, sa.ForeignKey("polymers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("property_definition_id", uuid_type, sa.ForeignKey("property_definitions.id"), nullable=False), sa.Column("value", sa.Float(), nullable=False), sa.Column("unit", sa.String(100), nullable=False),
        sa.Column("uncertainty", sa.Float()), sa.Column("uncertainty_type", sa.String(100)), sa.Column("provenance_type", sa.String(50), nullable=False), sa.Column("method", sa.String(255)),
        sa.Column("temperature", sa.Float()), sa.Column("temperature_unit", sa.String(50)), sa.Column("pressure", sa.Float()), sa.Column("pressure_unit", sa.String(50)), sa.Column("conditions", sa.JSON()),
        sa.Column("provenance_id", uuid_type, sa.ForeignKey("provenance.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("provenance_type IN ('experiment', 'simulation', 'prediction', 'literature', 'unknown')", name="ck_property_record_provenance_type"),
    )
    op.create_index("ix_property_records_polymer_id", "property_records", ["polymer_id"])
    op.create_index("ix_property_records_property_definition_id", "property_records", ["property_definition_id"])
    op.create_index("ix_property_records_provenance_id", "property_records", ["provenance_id"])


def downgrade() -> None:
    op.drop_table("property_records")
    op.drop_table("polymer_structures")
    op.drop_table("provenance")
    op.drop_table("property_definitions")
    op.drop_table("polymers")
