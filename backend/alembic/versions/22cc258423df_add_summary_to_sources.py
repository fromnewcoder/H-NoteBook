"""add_summary_to_sources

Revision ID: 22cc258423df
Revises: 0002
Create Date: 2026-04-11 03:51:01.710998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '22cc258423df'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new enum types (since export_jobs is empty, we can recreate)
    op.execute("DROP TYPE IF EXISTS exportformat")
    op.execute("DROP TYPE IF EXISTS jobstatus")
    op.execute("CREATE TYPE exportformat AS ENUM ('PDF', 'MIND_MAP', 'DOCX', 'PPTX', 'XLSX')")
    op.execute("CREATE TYPE jobstatus AS ENUM ('QUEUED', 'PROCESSING', 'DONE', 'FAILED')")

    # Alter export_jobs: drop default, alter type, set new default
    op.execute("ALTER TABLE export_jobs ALTER COLUMN format TYPE exportformat USING format::text::exportformat")
    op.execute("ALTER TABLE export_jobs ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE export_jobs ALTER COLUMN status TYPE jobstatus USING status::text::jobstatus")
    op.execute("ALTER TABLE export_jobs ALTER COLUMN status SET DEFAULT 'QUEUED'::jobstatus")

    # Alter chat_messages.role to VARCHAR (drop enum dependency)
    op.execute("ALTER TABLE chat_messages ALTER COLUMN role TYPE VARCHAR(20) USING role::VARCHAR(20)")

    # Drop old indexes
    op.drop_index('idx_chat_messages_notebook_id_created', table_name='chat_messages')
    op.drop_index('idx_notebooks_user_id', table_name='notebooks')
    op.drop_index('idx_sources_notebook_id', table_name='sources')

    # Add summary column
    op.add_column('sources', sa.Column('summary', sa.Text(), nullable=True))

    # Recreate indexes
    op.create_index('idx_chat_messages_notebook_id_created', 'chat_messages', ['notebook_id', 'created_at'], unique=False)
    op.create_index('idx_notebooks_user_id', 'notebooks', ['user_id'], unique=False)
    op.create_index('idx_sources_notebook_id', 'sources', ['notebook_id'], unique=False)

    # Drop old enum types (no longer used after column alterations)
    op.execute("DROP TYPE IF EXISTS job_status")
    op.execute("DROP TYPE IF EXISTS export_format")


def downgrade() -> None:
    # Create old enum types
    op.execute("CREATE TYPE job_status AS ENUM ('queued', 'processing', 'done', 'failed')")
    op.execute("CREATE TYPE export_format AS ENUM ('pdf', 'mind_map', 'docx', 'pptx', 'xlsx')")

    # Remove summary column
    op.drop_column('sources', 'summary')

    # Drop new indexes
    op.drop_index('idx_sources_notebook_id', table_name='sources')
    op.drop_index('idx_notebooks_user_id', table_name='notebooks')
    op.drop_index('idx_chat_messages_notebook_id_created', table_name='chat_messages')

    # Recreate old indexes
    op.create_index('idx_sources_notebook_id', 'sources', ['notebook_id'], unique=False)
    op.create_index('idx_notebooks_user_id', 'notebooks', ['user_id'], unique=False)
    op.create_index('idx_chat_messages_notebook_id_created', 'chat_messages', ['notebook_id', 'created_at'], unique=False)

    # Restore export_jobs columns to old enum types
    op.execute("ALTER TABLE export_jobs ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE export_jobs ALTER COLUMN status TYPE job_status USING status::text::job_status")
    op.execute("ALTER TABLE export_jobs ALTER COLUMN status SET DEFAULT 'queued'::job_status")
    op.execute("ALTER TABLE export_jobs ALTER COLUMN format TYPE export_format USING format::text::export_format")

    # Restore chat_messages.role
    op.execute("ALTER TABLE chat_messages ALTER COLUMN role TYPE message_role USING role::message_role")

    # Drop new enum types
    op.execute("DROP TYPE jobstatus")
    op.execute("DROP TYPE exportformat")
