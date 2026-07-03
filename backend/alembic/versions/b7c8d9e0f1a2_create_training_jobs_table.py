"""create training_jobs table

Revision ID: b7c8d9e0f1a2
Revises: 9f1a2b3c4d5e
Create Date: 2026-07-03 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.types


revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = '9f1a2b3c4d5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('training_jobs',
    sa.Column('id', app.types.GUID(), nullable=False),
    sa.Column('project_id', app.types.GUID(), nullable=False),
    sa.Column('dataset_version_id', app.types.GUID(), nullable=False),
    sa.Column('base_model_id', app.types.GUID(), nullable=False),
    sa.Column('trainer_id', app.types.GUID(), nullable=False),
    sa.Column('assigned_server_id', app.types.GUID(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('resource_requirement_json', sa.JSON(), nullable=False),
    sa.Column('training_config_json', sa.JSON(), nullable=False),
    sa.Column('failure_reason', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assigned_server_id'], ['training_servers.id'], ),
    sa.ForeignKeyConstraint(['base_model_id'], ['base_models.id'], ),
    sa.ForeignKeyConstraint(['dataset_version_id'], ['dataset_versions.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['trainer_id'], ['trainer_registry.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_jobs_dataset_version_id'), 'training_jobs', ['dataset_version_id'], unique=False)
    op.create_index(op.f('ix_training_jobs_project_id'), 'training_jobs', ['project_id'], unique=False)
    op.create_index(op.f('ix_training_jobs_status'), 'training_jobs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_training_jobs_status'), table_name='training_jobs')
    op.drop_index(op.f('ix_training_jobs_project_id'), table_name='training_jobs')
    op.drop_index(op.f('ix_training_jobs_dataset_version_id'), table_name='training_jobs')
    op.drop_table('training_jobs')

