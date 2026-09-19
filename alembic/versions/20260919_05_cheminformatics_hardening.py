"""harden persisted cheminformatics metadata

Revision ID: 20260919_05
Revises: 20260919_04
"""
from alembic import op

revision = "20260919_05"
down_revision = "20260919_04"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("polymer_structures") as batch:
        batch.create_check_constraint("ck_structure_validation_status", "validation_status IN ('not_validated', 'valid', 'partially_valid', 'invalid', 'unsupported')")
        batch.create_check_constraint("ck_structure_connection_point_count_nonnegative", "connection_point_count IS NULL OR connection_point_count >= 0")


def downgrade():
    with op.batch_alter_table("polymer_structures") as batch:
        batch.drop_constraint("ck_structure_connection_point_count_nonnegative", type_="check")
        batch.drop_constraint("ck_structure_validation_status", type_="check")
