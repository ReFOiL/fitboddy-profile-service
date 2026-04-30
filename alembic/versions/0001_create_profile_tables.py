"""create profile tables

Revision ID: 0001_create_profile_tables
Revises:
Create Date: 2026-04-27 03:35:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_profile_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "client_profiles",
        sa.Column("profile_id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("goal", sa.String(length=120), nullable=False),
        sa.Column("experience_level", sa.String(length=32), nullable=False),
        sa.Column("equipment_json", sa.Text(), nullable=False),
        sa.Column("limitations", sa.Text(), nullable=True),
        sa.Column("medical_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("profile_id"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_client_profiles_tenant_user"),
    )
    op.create_index("ix_client_profiles_tenant_id", "client_profiles", ["tenant_id"], unique=False)
    op.create_index("ix_client_profiles_user_id", "client_profiles", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_client_profiles_user_id", table_name="client_profiles")
    op.drop_index("ix_client_profiles_tenant_id", table_name="client_profiles")
    op.drop_table("client_profiles")
