"""create checkpoints table

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-07-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.types


revision: str = "d2e3f4a5b6c7"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "checkpoints",
        sa.Column("id", app.types.GUID(), nullable=False),
        sa.Column("project_id", app.types.GUID(), nullable=False),
        sa.Column("training_job_id", app.types.GUID(), nullable=False),
        sa.Column("checkpoint_path", sa.String(length=500), nullable=False),
        sa.Column("epoch", sa.Integer(), nullable=True),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.Column("is_latest", sa.Boolean(), nullable=False),
        sa.Column("is_best", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["training_job_id"], ["training_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_checkpoints_project_id"), "checkpoints", ["project_id"], unique=False)
    op.create_index(op.f("ix_checkpoints_training_job_id"), "checkpoints", ["training_job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_checkpoints_training_job_id"), table_name="checkpoints")
    op.drop_index(op.f("ix_checkpoints_project_id"), table_name="checkpoints")
    op.drop_table("checkpoints")
