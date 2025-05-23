"""Add provider_id to Booking

Revision ID: 19007fa49fcc
Revises: 9f4036b7547f
Create Date: 2025-04-07 12:12:41.461843

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19007fa49fcc'
down_revision = '9f4036b7547f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('provided_services', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('provided_services')

    # ### end Alembic commands ###
