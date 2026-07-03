"""create training_servers table

Revision ID: 9f1a2b3c4d5e
Revises: 02cee7ccc202
Create Date: 2026-07-03 09:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import app.types


revision: str = '9f1a2b3c4d5e'
down_revision: Union[str, None] = '02cee7ccc202'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('training_servers',
    sa.Column('id', app.types.GUID(), nullable=False),
    sa.Column('hostname', sa.String(length=255), nullable=False),
    sa.Column('ip_address', sa.String(length=64), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('gpu_count', sa.Integer(), nullable=False),
    sa.Column('gpu_memory_total_gb', sa.Float(), nullable=False),
    sa.Column('gpu_memory_free_gb', sa.Float(), nullable=False),
    sa.Column('gpu_utilization_percent', sa.Float(), nullable=False),
    sa.Column('cpu_usage_percent', sa.Float(), nullable=False),
    sa.Column('ram_total_gb', sa.Float(), nullable=False),
    sa.Column('ram_free_gb', sa.Float(), nullable=False),
    sa.Column('disk_free_gb', sa.Float(), nullable=False),
    sa.Column('running_job_count', sa.Integer(), nullable=False),
    sa.Column('max_concurrent_jobs', sa.Integer(), nullable=False),
    sa.Column('last_heartbeat_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_servers_hostname'), 'training_servers', ['hostname'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_training_servers_hostname'), table_name='training_servers')
    op.drop_table('training_servers')

