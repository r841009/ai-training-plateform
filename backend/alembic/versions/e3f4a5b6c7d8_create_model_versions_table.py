"""create model_versions table

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-07-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.types


revision: str = "e3f4a5b6c7d8"
down_revision: Union[str, None] = "d2e3f4a5b6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "model_versions",
        sa.Column("id", app.types.GUID(), nullable=False),
        sa.Column("project_id", app.types.GUID(), nullable=False),
        sa.Column("training_job_id", app.types.GUID(), nullable=False),
        sa.Column("dataset_version_id", app.types.GUID(), nullable=False),
        sa.Column("base_model_id", app.types.GUID(), nullable=False),
        sa.Column("parent_model_version_id", app.types.GUID(), nullable=True),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("artifact_path", sa.String(length=500), nullable=False),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["base_model_id"], ["base_models.id"]),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_versions.id"]),
        sa.ForeignKeyConstraint(["parent_model_version_id"], ["model_versions.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["training_job_id"], ["training_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "version_no", name="uq_model_versions_project_version"),
        sa.UniqueConstraint("training_job_id", name="uq_model_versions_training_job"),
    )
    op.create_index(op.f("ix_model_versions_project_id"), "model_versions", ["project_id"], unique=False)
    op.create_index(op.f("ix_model_versions_training_job_id"), "model_versions", ["training_job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_model_versions_training_job_id"), table_name="model_versions")
    op.drop_index(op.f("ix_model_versions_project_id"), table_name="model_versions")
    op.drop_table("model_versions")
