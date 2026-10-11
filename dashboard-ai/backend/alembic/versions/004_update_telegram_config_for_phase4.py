"""update telegram_config for phase4

Revision ID: 004
Revises: 
Create Date: 2026-10-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = None  # This is the first migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to telegram_config if they don't exist
    # First check if table exists, if not the columns will be created by Base
    try:
        op.add_column('telegram_config', sa.Column('bot_id', sa.BigInteger(), nullable=True))
    except:
        pass
    
    try:
        op.add_column('telegram_config', sa.Column('bot_name', sa.String(), nullable=True))
    except:
        pass
    
    try:
        op.add_column('telegram_config', sa.Column('combo_id', sa.String(), nullable=True))
    except:
        pass
    
    try:
        op.add_column('telegram_config', sa.Column('last_update_id', sa.BigInteger(), server_default='0', nullable=True))
    except:
        pass


def downgrade() -> None:
    # Remove new columns
    with op.batch_alter_table('telegram_config') as batch_op:
        try:
            batch_op.drop_column('last_update_id')
        except:
            pass
        try:
            batch_op.drop_column('combo_id')
        except:
            pass
        try:
            batch_op.drop_column('bot_name')
        except:
            pass
        try:
            batch_op.drop_column('bot_id')
        except:
            pass
