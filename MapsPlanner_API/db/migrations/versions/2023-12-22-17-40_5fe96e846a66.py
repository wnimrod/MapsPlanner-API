"""empty message

Revision ID: 5fe96e846a66
Revises: d774b20ea55c
Create Date: 2023-12-22 17:40:24.661131

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5fe96e846a66"
down_revision = "d774b20ea55c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "session",
        sa.Column("token", sa.String(), nullable=False),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("token"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("session")
    # ### end Alembic commands ###