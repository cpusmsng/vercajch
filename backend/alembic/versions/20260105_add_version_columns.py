"""Add version columns for optimistic locking

Revision ID: 20260105_add_version
Revises:
Create Date: 2026-01-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260105_add_version'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add version column to equipment table
    op.add_column('equipment', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))

    # Add version column to locations table
    op.add_column('locations', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))

    # Add version column to users table
    op.add_column('users', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    op.drop_column('users', 'version')
    op.drop_column('locations', 'version')
    op.drop_column('equipment', 'version')
