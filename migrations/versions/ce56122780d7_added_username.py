"""added username field

Revision ID: ce56122780d7
Revises: 9f6a703aef13
Create Date: 2023-08-06 11:42:20.171228

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ce56122780d7"
down_revision = "9f6a703aef13"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("username", sa.String(length=20), nullable=False))
        batch_op.create_unique_constraint(None, ["username"])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="unique")
        batch_op.drop_column("username")

    # ### end Alembic commands ###
