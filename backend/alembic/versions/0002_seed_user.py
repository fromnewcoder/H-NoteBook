"""Seed user

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create seed user with default password
    # Password hash is for 'changeme123' - should be overridden via env var in production
    hashed_pw = pwd_context.hash('changeme123')
    op.execute(f"""
        INSERT INTO users (id, username, hashed_pw)
        VALUES (
            gen_random_uuid(),
            'admin',
            '{hashed_pw}'
        )
        ON CONFLICT (username) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("DELETE FROM users WHERE username = 'admin'")
