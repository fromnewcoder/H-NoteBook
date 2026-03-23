"""Initial migration

Revision ID: 0001
Revises:
Create Date: 2026-03-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    source_type = postgresql.ENUM('url', 'txt', 'md', 'docx', name='source_type', create_type=False)
    source_type.create(op.get_bind(), checkfirst=True)

    source_status = postgresql.ENUM('processing', 'ready', 'failed', name='source_status', create_type=False)
    source_status.create(op.get_bind(), checkfirst=True)

    message_role = postgresql.ENUM('user', 'assistant', name='message_role', create_type=False)
    message_role.create(op.get_bind(), checkfirst=True)

    export_format = postgresql.ENUM('pdf', 'mind_map', 'docx', 'pptx', 'xlsx', name='export_format', create_type=False)
    export_format.create(op.get_bind(), checkfirst=True)

    job_status = postgresql.ENUM('queued', 'processing', 'done', 'failed', name='job_status', create_type=False)
    job_status.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('username', sa.String(64), nullable=False, unique=True),
        sa.Column('hashed_pw', sa.String(256), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )

    # Create notebooks table
    op.create_table(
        'notebooks',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False, server_default='Untitled Notebook'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_notebooks_user_id', 'notebooks', ['user_id'])

    # Create sources table
    op.create_table(
        'sources',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('notebook_id', sa.UUID(), sa.ForeignKey('notebooks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_type', postgresql.ENUM('url', 'txt', 'md', 'docx', name='source_type', create_type=False), nullable=False),
        sa.Column('name', sa.String(512), nullable=False),
        sa.Column('raw_content', sa.Text()),
        sa.Column('status', postgresql.ENUM('processing', 'ready', 'failed', name='source_status', create_type=False), nullable=False, server_default='processing'),
        sa.Column('error_message', sa.Text()),
        sa.Column('chunk_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_sources_notebook_id', 'sources', ['notebook_id'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('notebook_id', sa.UUID(), sa.ForeignKey('notebooks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', postgresql.ENUM('user', 'assistant', name='message_role', create_type=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_ids', postgresql.ARRAY(sa.UUID()), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_chat_messages_notebook_id_created', 'chat_messages', ['notebook_id', 'created_at'])

    # Create export_jobs table
    op.create_table(
        'export_jobs',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('notebook_id', sa.UUID(), sa.ForeignKey('notebooks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('format', postgresql.ENUM('pdf', 'mind_map', 'docx', 'pptx', 'xlsx', name='export_format', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('queued', 'processing', 'done', 'failed', name='job_status', create_type=False), nullable=False, server_default='queued'),
        sa.Column('file_path', sa.String(512)),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table('export_jobs')
    op.drop_table('chat_messages')
    op.drop_table('sources')
    op.drop_table('notebooks')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS job_status')
    op.execute('DROP TYPE IF EXISTS export_format')
    op.execute('DROP TYPE IF EXISTS message_role')
    op.execute('DROP TYPE IF EXISTS source_status')
    op.execute('DROP TYPE IF EXISTS source_type')
