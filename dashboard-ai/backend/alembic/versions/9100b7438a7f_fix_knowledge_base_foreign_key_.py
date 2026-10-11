"""fix_knowledge_base_foreign_key_constraints

Revision ID: 9100b7438a7f
Revises: 006
Create Date: 2026-10-01 17:51:27.154260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9100b7438a7f'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Fix foreign key constraints for knowledge base deletion.
    
    1. token_usage.knowledge_base_id: ON DELETE SET NULL
       (preserve analytics history when KB is deleted)
    
    2. documents.knowledge_base_id: ON DELETE CASCADE
       (delete documents when KB is deleted)
    
    3. document_chunks.document_id: ON DELETE CASCADE
       (delete chunks when document is deleted)
    """
    
    # Fix token_usage FK: ON DELETE SET NULL
    op.drop_constraint('token_usage_knowledge_base_id_fkey', 'token_usage', type_='foreignkey')
    op.create_foreign_key(
        'token_usage_knowledge_base_id_fkey',
        'token_usage',
        'knowledge_bases',
        ['knowledge_base_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Fix documents FK: ON DELETE CASCADE
    op.drop_constraint('documents_knowledge_base_id_fkey', 'documents', type_='foreignkey')
    op.create_foreign_key(
        'documents_knowledge_base_id_fkey',
        'documents',
        'knowledge_bases',
        ['knowledge_base_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Fix document_chunks FK: ON DELETE CASCADE
    op.drop_constraint('document_chunks_document_id_fkey', 'document_chunks', type_='foreignkey')
    op.create_foreign_key(
        'document_chunks_document_id_fkey',
        'document_chunks',
        'documents',
        ['document_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Revert to original NO ACTION constraints."""
    
    # Revert token_usage FK
    op.drop_constraint('token_usage_knowledge_base_id_fkey', 'token_usage', type_='foreignkey')
    op.create_foreign_key(
        'token_usage_knowledge_base_id_fkey',
        'token_usage',
        'knowledge_bases',
        ['knowledge_base_id'],
        ['id']
    )
    
    # Revert documents FK
    op.drop_constraint('documents_knowledge_base_id_fkey', 'documents', type_='foreignkey')
    op.create_foreign_key(
        'documents_knowledge_base_id_fkey',
        'documents',
        'knowledge_bases',
        ['knowledge_base_id'],
        ['id']
    )
    
    # Revert document_chunks FK
    op.drop_constraint('document_chunks_document_id_fkey', 'document_chunks', type_='foreignkey')
    op.create_foreign_key(
        'document_chunks_document_id_fkey',
        'document_chunks',
        'documents',
        ['document_id'],
        ['id']
    )
