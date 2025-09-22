"""Add is_admin field to User

Revision ID: 6249e8d7aa53
Revises: 
Create Date: 2025-09-17 12:01:50.868801

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '6249e8d7aa53'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'is_admin' not in columns:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='false'))
    
    # Atualiza os registros existentes para não terem is_admin como nulo
    op.execute('UPDATE users SET is_admin = false WHERE is_admin IS NULL')
    
    # Altera a coluna para não permitir nulos
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('is_admin', existing_type=sa.Boolean(), nullable=False)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'is_admin' in columns:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.drop_column('is_admin')