"""Added birthday and gender fields

Revision ID: 03533ceead47
Revises: 498cdd2ee6b2
Create Date: 2024-01-11 20:39:04.908177

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ChoiceType

import enum

# revision identifiers, used by Alembic.
revision = "03533ceead47"
down_revision = "498cdd2ee6b2"
branch_labels = None
depends_on = None


class EGender(enum.Enum):
    male = "M"
    female = "F"


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "gender",
            ChoiceType(EGender, impl=sa.Integer()),
            nullable=True,
        ),
    )
    op.add_column(
        "users", sa.Column("birth_date", sa.DateTime(timezone=True), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "birth_date")
    op.drop_column("users", "gender")
    # ### end Alembic commands ###
