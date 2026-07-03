"""add base model license fields

Revision ID: c1d2e3f4a5b6
Revises: b7c8d9e0f1a2
Create Date: 2026-07-03 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('base_models', sa.Column('source_provider', sa.String(length=128), server_default='unknown', nullable=False))
    op.add_column('base_models', sa.Column('license_name', sa.String(length=128), server_default='UNKNOWN', nullable=False))
    op.add_column('base_models', sa.Column('license_url', sa.String(length=500), nullable=True))
    op.add_column('base_models', sa.Column('license_risk_level', sa.String(length=32), server_default='UNKNOWN', nullable=False))
    op.add_column('base_models', sa.Column('commercial_use_allowed', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('base_models', sa.Column('oem_use_allowed', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('base_models', sa.Column('requires_enterprise_license', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('base_models', sa.Column('license_notes', sa.Text(), nullable=True))

    op.execute(
        """
        UPDATE base_models
        SET source_provider = 'Ultralytics',
            license_name = 'AGPL-3.0 / Ultralytics Enterprise License',
            license_url = 'https://www.ultralytics.com/license',
            license_risk_level = 'HIGH',
            commercial_use_allowed = false,
            oem_use_allowed = false,
            requires_enterprise_license = true,
            license_notes = 'Do not use in OEM/proprietary/customer-facing deployments unless an Ultralytics Enterprise License covers the project.'
        WHERE name IN ('yolov8n', 'yolov8s', 'yolov11n')
        """
    )
    op.execute(
        """
        UPDATE base_models
        SET source_provider = 'torchvision',
            license_name = 'BSD-3-Clause',
            license_url = 'https://github.com/pytorch/vision/blob/main/LICENSE',
            license_risk_level = 'LOW',
            commercial_use_allowed = true,
            oem_use_allowed = true,
            requires_enterprise_license = false,
            license_notes = 'Permissive license; retain required copyright and license notices.'
        WHERE name = 'resnet50'
        """
    )
    op.execute(
        """
        UPDATE base_models
        SET source_provider = 'torchvision',
            license_name = 'BSD-3-Clause',
            license_url = 'https://github.com/pytorch/vision/blob/main/LICENSE',
            license_risk_level = 'LOW',
            commercial_use_allowed = true,
            oem_use_allowed = true,
            requires_enterprise_license = false,
            license_notes = 'Use torchvision implementation/weights or re-verify the final source before release.'
        WHERE name = 'efficientnet'
        """
    )
    op.execute(
        """
        UPDATE base_models
        SET source_provider = 'internal',
            license_name = 'Internal implementation',
            license_url = null,
            license_risk_level = 'LOW',
            commercial_use_allowed = true,
            oem_use_allowed = true,
            requires_enterprise_license = false,
            license_notes = 'Use company-owned implementation/weights or re-verify any third-party implementation before release.'
        WHERE name = 'unet'
        """
    )


def downgrade() -> None:
    op.drop_column('base_models', 'license_notes')
    op.drop_column('base_models', 'requires_enterprise_license')
    op.drop_column('base_models', 'oem_use_allowed')
    op.drop_column('base_models', 'commercial_use_allowed')
    op.drop_column('base_models', 'license_risk_level')
    op.drop_column('base_models', 'license_url')
    op.drop_column('base_models', 'license_name')
    op.drop_column('base_models', 'source_provider')

