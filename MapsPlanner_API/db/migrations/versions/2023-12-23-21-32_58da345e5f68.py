"""Added is_administrator to user model

Revision ID: 58da345e5f68
Revises: a4d20cd9442d
Create Date: 2023-12-23 21:32:27.177600

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = "58da345e5f68"
down_revision = "a4d20cd9442d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "is_administrator",
            sa.Boolean(),
            nullable=False,
            server_default=expression.false(),
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "is_administrator")
    # ### end Alembic commands ###
