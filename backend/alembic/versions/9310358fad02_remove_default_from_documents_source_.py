"""remove_default_from_documents_source_and_backfill

Revision ID: 9310358fad02
Revises: 4692cf7c6555
Create Date: 2026-09-27 16:46:22.018768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9310358fad02'
down_revision: Union[str, Sequence[str], None] = '4692cf7c6555'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('documents', 'source', server_default=None)
    op.execute("UPDATE documents SET source = 'MOCK' WHERE file_path IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE documents SET source = NULL WHERE source = 'MOCK' AND file_path IS NULL")
