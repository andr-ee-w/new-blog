"""Added Posts Model

Revision ID: 9f6a703aef13
Revises: ef61fb9d3f90
Create Date: 2023-08-04 08:28:58.342026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f6a703aef13"
down_revision = "ef61fb9d3f90"
branch_labels = None
depends_on = None


def upgrade():
    # Create the 'Posts' table
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column(
            "date_posted",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("slug", sa.String(length=255), nullable=False),
    )


def downgrade():
    pass
