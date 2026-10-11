"""add user_id to knowledge_bases

Revision ID: 006
Revises: 005
Create Date: 2026-10-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add user_id column to knowledge_bases
    op.add_column('knowledge_bases', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Set default user_id for existing records (user 1)
    op.execute("UPDATE knowledge_bases SET user_id = 1 WHERE user_id IS NULL")
    
    # Make user_id NOT NULL after setting defaults
    op.alter_column('knowledge_bases', 'user_id', nullable=False)
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_knowledge_bases_user',
        'knowledge_bases',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Add index
    op.create_index(op.f('ix_knowledge_bases_user_id'), 'knowledge_bases', ['user_id'], unique=False)


def downgrade():
    # Remove index
    op.drop_index(op.f('ix_knowledge_bases_user_id'), table_name='knowledge_bases')
    
    # Remove foreign key
    op.drop_constraint('fk_knowledge_bases_user', 'knowledge_bases', type_='foreignkey')
    
    # Remove column
    op.drop_column('knowledge_bases', 'user_id')
