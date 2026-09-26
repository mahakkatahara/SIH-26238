"""add user_id to students

Revision ID: 4bc99020e660
Revises: 511ba582cdb2
Create Date: 2026-09-27 02:40:47.421445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bc99020e660'
down_revision: Union[str, Sequence[str], None] = '511ba582cdb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('students', sa.Column('user_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_students_user_id', 'students', ['user_id'])
    op.create_foreign_key('fk_students_user_id_users', 'students', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_students_user_id_users', 'students', type_='foreignkey')
    op.drop_constraint('uq_students_user_id', 'students', type_='unique')
    op.drop_column('students', 'user_id')
