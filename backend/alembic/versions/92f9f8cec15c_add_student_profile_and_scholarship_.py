"""add_student_profile_and_scholarship_rules

Revision ID: 92f9f8cec15c
Revises: 9ab96959d7f3
Create Date: 2026-09-27 14:57:40.076360

"""
import json
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '92f9f8cec15c'
down_revision: Union[str, Sequence[str], None] = '9ab96959d7f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to students table
    op.add_column('students', sa.Column('tribe_status', sa.String(), nullable=True))
    op.add_column('students', sa.Column('state', sa.String(), nullable=True))
    op.add_column('students', sa.Column('annual_family_income', sa.Integer(), nullable=True))
    op.add_column('students', sa.Column('education_level', sa.String(), nullable=True))
    op.add_column('students', sa.Column('institution_name', sa.String(), nullable=True))
    op.add_column('students', sa.Column('is_hosteller', sa.Boolean(), nullable=True))
    op.add_column('students', sa.Column('date_of_birth', sa.Date(), nullable=True))

    # Add columns to scholarships table
    op.add_column('scholarships', sa.Column('scheme_type', sa.String(), nullable=True))
    op.add_column('scholarships', sa.Column('income_ceiling', sa.Integer(), nullable=True))
    op.add_column('scholarships', sa.Column('eligible_levels', sa.JSON(), nullable=True))
    op.add_column('scholarships', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')))

    # Seed / Update 5 MoTA scholarship schemes
    conn = op.get_bind()
    scholarships_table = table(
        'scholarships',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('scheme_type', sa.String),
        column('income_ceiling', sa.Integer),
        column('eligible_levels', sa.JSON),
        column('is_active', sa.Boolean),
    )

    # 1. Update existing POST_MATRIC (or POST_MATRIC_ST) if exists, else insert
    post_matric_levels = [
        "CLASS_11", "CLASS_12", "ITI", "DIPLOMA", "UG", "PG", "MPHIL", "PHD", "POSTDOC"
    ]
    existing_pm = conn.execute(
        sa.text("SELECT id FROM scholarships WHERE code IN ('POST_MATRIC', 'POST_MATRIC_ST')")
    ).fetchone()

    if existing_pm:
        conn.execute(
            sa.text(
                "UPDATE scholarships SET "
                "code = 'POST_MATRIC_ST', "
                "name = 'Post-Matric Scholarship for ST Students', "
                "scheme_type = 'CSS', "
                "income_ceiling = 250000, "
                "eligible_levels = :levels, "
                "is_active = true "
                "WHERE id = :id"
            ),
            {"levels": json.dumps(post_matric_levels), "id": existing_pm[0]}
        )
    else:
        conn.execute(
            scholarships_table.insert().values(
                id=str(uuid.uuid4()),
                code='POST_MATRIC_ST',
                name='Post-Matric Scholarship for ST Students',
                scheme_type='CSS',
                income_ceiling=250000,
                eligible_levels=post_matric_levels,
                is_active=True
            )
        )

    # Other schemes to seed
    schemes_to_seed = [
        {
            "code": "PRE_MATRIC_ST",
            "name": "Pre-Matric Scholarship for ST Students",
            "scheme_type": "CSS",
            "income_ceiling": 250000,
            "eligible_levels": ["CLASS_9", "CLASS_10"],
            "is_active": True
        },
        {
            "code": "TOP_CLASS_ST",
            "name": "National Scholarship for Higher Education of ST Students (Top Class)",
            "scheme_type": "CENTRAL_SECTOR",
            "income_ceiling": 600000,
            "eligible_levels": ["UG", "PG", "MPHIL", "PHD"],
            "is_active": True
        },
        {
            "code": "NATIONAL_FELLOWSHIP_ST",
            "name": "National Fellowship for ST Students (NFST)",
            "scheme_type": "CENTRAL_SECTOR",
            "income_ceiling": None,
            "eligible_levels": ["MPHIL", "PHD"],
            "is_active": True
        },
        {
            "code": "NATIONAL_OVERSEAS_ST",
            "name": "National Overseas Scholarship for ST Students (NOS)",
            "scheme_type": "CENTRAL_SECTOR",
            "income_ceiling": 600000,
            "eligible_levels": ["PG", "PHD", "POSTDOC"],
            "is_active": True
        },
    ]

    for scheme in schemes_to_seed:
        existing = conn.execute(
            sa.text("SELECT id FROM scholarships WHERE code = :code"),
            {"code": scheme["code"]}
        ).fetchone()
        if not existing:
            conn.execute(
                scholarships_table.insert().values(
                    id=str(uuid.uuid4()),
                    code=scheme["code"],
                    name=scheme["name"],
                    scheme_type=scheme["scheme_type"],
                    income_ceiling=scheme["income_ceiling"],
                    eligible_levels=scheme["eligible_levels"],
                    is_active=scheme["is_active"]
                )
            )


def downgrade() -> None:
    op.drop_column('scholarships', 'is_active')
    op.drop_column('scholarships', 'eligible_levels')
    op.drop_column('scholarships', 'income_ceiling')
    op.drop_column('scholarships', 'scheme_type')

    op.drop_column('students', 'date_of_birth')
    op.drop_column('students', 'is_hosteller')
    op.drop_column('students', 'institution_name')
    op.drop_column('students', 'education_level')
    op.drop_column('students', 'annual_family_income')
    op.drop_column('students', 'state')
    op.drop_column('students', 'tribe_status')
