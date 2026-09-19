"""harden scientific polymer data integrity

Revision ID: 20260919_02
Revises: 20260919_01
Create Date: 2026-09-19
"""

from alembic import context, op
import sqlalchemy as sa


revision = "20260919_02"
down_revision = "20260919_01"
branch_labels = None
depends_on = None

POLYMER_CHECKS = (
    ("ck_polymer_mn_positive", "number_average_molecular_weight IS NULL OR number_average_molecular_weight > 0"),
    ("ck_polymer_mw_positive", "weight_average_molecular_weight IS NULL OR weight_average_molecular_weight > 0"),
    ("ck_polymer_dispersity_positive", "dispersity IS NULL OR dispersity > 0"),
    ("ck_polymer_dp_positive", "degree_of_polymerization IS NULL OR degree_of_polymerization > 0"),
)


def upgrade() -> None:
    dialect = context.get_context().dialect.name
    with op.batch_alter_table("polymers", recreate="always" if dialect == "sqlite" else "auto") as batch:
        for name, condition in POLYMER_CHECKS:
            batch.create_check_constraint(name, condition)

    if dialect == "sqlite":
        convention = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}
        with op.batch_alter_table("property_records", recreate="always", naming_convention=convention) as batch:
            batch.drop_constraint("fk_property_records_property_definition_id_property_definitions", type_="foreignkey")
            batch.drop_constraint("fk_property_records_provenance_id_provenance", type_="foreignkey")
            batch.create_foreign_key("fk_property_records_property_definition_id_property_definitions", "property_definitions", ["property_definition_id"], ["id"], ondelete="RESTRICT")
            batch.create_foreign_key("fk_property_records_provenance_id_provenance", "provenance", ["provenance_id"], ["id"], ondelete="RESTRICT")
            batch.create_check_constraint("ck_property_record_uncertainty_nonnegative", "uncertainty IS NULL OR uncertainty >= 0")
    else:
        op.drop_constraint("property_records_property_definition_id_fkey", "property_records", type_="foreignkey")
        op.drop_constraint("property_records_provenance_id_fkey", "property_records", type_="foreignkey")
        op.create_foreign_key("fk_property_records_property_definition_id_property_definitions", "property_records", "property_definitions", ["property_definition_id"], ["id"], ondelete="RESTRICT")
        op.create_foreign_key("fk_property_records_provenance_id_provenance", "property_records", "provenance", ["provenance_id"], ["id"], ondelete="RESTRICT")
        op.create_check_constraint("ck_property_record_uncertainty_nonnegative", "property_records", "uncertainty IS NULL OR uncertainty >= 0")


def downgrade() -> None:
    dialect = context.get_context().dialect.name
    if dialect == "sqlite":
        convention = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}
        with op.batch_alter_table("property_records", recreate="always", naming_convention=convention) as batch:
            batch.drop_constraint("fk_property_records_property_definition_id_property_definitions", type_="foreignkey")
            batch.drop_constraint("fk_property_records_provenance_id_provenance", type_="foreignkey")
            batch.drop_constraint("ck_property_record_uncertainty_nonnegative", type_="check")
            batch.create_foreign_key("fk_property_records_property_definition_id_property_definitions", "property_definitions", ["property_definition_id"], ["id"])
            batch.create_foreign_key("fk_property_records_provenance_id_provenance", "provenance", ["provenance_id"], ["id"])
    else:
        op.drop_constraint("fk_property_records_property_definition_id_property_definitions", "property_records", type_="foreignkey")
        op.drop_constraint("fk_property_records_provenance_id_provenance", "property_records", type_="foreignkey")
        op.drop_constraint("ck_property_record_uncertainty_nonnegative", "property_records", type_="check")
        op.create_foreign_key("property_records_property_definition_id_fkey", "property_records", "property_definitions", ["property_definition_id"], ["id"])
        op.create_foreign_key("property_records_provenance_id_fkey", "property_records", "provenance", ["provenance_id"], ["id"])
    with op.batch_alter_table("polymers", recreate="always" if dialect == "sqlite" else "auto") as batch:
        for name, _condition in POLYMER_CHECKS:
            batch.drop_constraint(name, type_="check")
