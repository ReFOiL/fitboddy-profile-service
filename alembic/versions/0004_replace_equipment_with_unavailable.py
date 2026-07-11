"""Replace profile equipment_json with unavailable_equipment_json

Revision ID: 0004_unavailable_equipment
Revises: 0003_profile_workout_location
Create Date: 2026-07-12 00:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_unavailable_equipment"
down_revision = "0003_profile_workout_location"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("client_profiles") as batch_op:
        batch_op.add_column(
            sa.Column(
                "unavailable_equipment_json",
                sa.Text(),
                nullable=False,
                server_default="[]",
            )
        )
        batch_op.drop_column("equipment_json")


def downgrade() -> None:
    with op.batch_alter_table("client_profiles") as batch_op:
        batch_op.add_column(
            sa.Column(
                "equipment_json",
                sa.Text(),
                nullable=False,
                server_default="[]",
            )
        )
        batch_op.drop_column("unavailable_equipment_json")
