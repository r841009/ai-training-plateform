"""create evaluation tables

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-07-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.types


revision: str = "f4a5b6c7d8e9"
down_revision: Union[str, None] = "e3f4a5b6c7d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evaluation_datasets",
        sa.Column("id", app.types.GUID(), nullable=False),
        sa.Column("project_id", app.types.GUID(), nullable=False),
        sa.Column("dataset_version_id", app.types.GUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_versions.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evaluation_datasets_project_id"), "evaluation_datasets", ["project_id"], unique=False)

    op.create_table(
        "evaluation_results",
        sa.Column("id", app.types.GUID(), nullable=False),
        sa.Column("project_id", app.types.GUID(), nullable=False),
        sa.Column("model_version_id", app.types.GUID(), nullable=False),
        sa.Column("dataset_version_id", app.types.GUID(), nullable=True),
        sa.Column("evaluation_dataset_id", app.types.GUID(), nullable=True),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.Column("report_path", sa.String(length=500), nullable=True),
        sa.Column("sample_predictions_path", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_versions.id"]),
        sa.ForeignKeyConstraint(["evaluation_dataset_id"], ["evaluation_datasets.id"]),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evaluation_results_project_id"), "evaluation_results", ["project_id"], unique=False)
    op.create_index(
        op.f("ix_evaluation_results_model_version_id"), "evaluation_results", ["model_version_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_evaluation_results_model_version_id"), table_name="evaluation_results")
    op.drop_index(op.f("ix_evaluation_results_project_id"), table_name="evaluation_results")
    op.drop_table("evaluation_results")
    op.drop_index(op.f("ix_evaluation_datasets_project_id"), table_name="evaluation_datasets")
    op.drop_table("evaluation_datasets")
