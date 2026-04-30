"""add personal fields to client profiles

Revision ID: 0002_profile_personal_fields
Revises: 0001_create_profile_tables
Create Date: 2026-04-29 05:58:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_profile_personal_fields"
down_revision = "0001_create_profile_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("client_profiles", sa.Column("full_name", sa.String(length=120), nullable=True))
    op.add_column("client_profiles", sa.Column("avatar_url", sa.String(length=500), nullable=True))
    op.add_column("client_profiles", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column("client_profiles", sa.Column("bio", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("client_profiles", "bio")
    op.drop_column("client_profiles", "city")
    op.drop_column("client_profiles", "avatar_url")
    op.drop_column("client_profiles", "full_name")
