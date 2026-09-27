"""add_file_path_and_source_to_documents

Revision ID: 4692cf7c6555
Revises: 1f2eea94b2a4
Create Date: 2026-09-27 15:31:58.770017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4692cf7c6555'
down_revision: Union[str, Sequence[str], None] = '1f2eea94b2a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('documents', sa.Column('file_path', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('source', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('documents', 'source')
    op.drop_column('documents', 'file_path')
