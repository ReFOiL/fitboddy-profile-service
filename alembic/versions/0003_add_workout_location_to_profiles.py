"""add workout location to profiles

Revision ID: 0003_profile_workout_location
Revises: 0002_profile_personal_fields
Create Date: 2026-04-29 08:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_profile_workout_location"
down_revision = "0002_profile_personal_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("client_profiles", sa.Column("workout_location", sa.String(length=16), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("client_profiles", "workout_location")
