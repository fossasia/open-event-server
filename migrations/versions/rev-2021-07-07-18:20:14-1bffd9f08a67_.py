"""empty message

Revision ID: 1bffd9f08a67
Revises: eecca008e169
Create Date: 2021-07-07 18:20:14.769144

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '1bffd9f08a67'
down_revision = 'eecca008e169'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('multiple_slides_url', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'multiple_slides_url')
    # ### end Alembic commands ###
