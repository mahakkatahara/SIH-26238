"""add_study_country_to_students

Revision ID: 1f2eea94b2a4
Revises: 92f9f8cec15c
Create Date: 2026-09-27 15:24:29.752109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f2eea94b2a4'
down_revision: Union[str, Sequence[str], None] = '92f9f8cec15c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('students', sa.Column('study_country', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('students', 'study_country')
