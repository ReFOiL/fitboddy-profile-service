"""add age and gender to client profiles

Revision ID: 0005_profile_age_gender
Revises: 0004_unavailable_equipment
Create Date: 2026-07-18 17:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_profile_age_gender"
down_revision = "0004_unavailable_equipment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("client_profiles", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column(
        "client_profiles",
        sa.Column("gender", sa.String(length=16), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("client_profiles", "gender")
    op.drop_column("client_profiles", "age")
