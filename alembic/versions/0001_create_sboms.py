# alembic/versions/0001_create_sboms.py
"""create sboms table

Revision ID: 0001_create_sboms
Revises: 
Create Date: 2025-10-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '0001_create_sboms'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'sboms',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_name', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('sbom', pg.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('summary', pg.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('object_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_sboms_project_created', 'sboms', ['project_name', 'created_at'])

def downgrade():
    op.drop_index('ix_sboms_project_created', table_name='sboms')
    op.drop_table('sboms')
