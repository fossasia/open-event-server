"""empty message

Revision ID: f52267133dcc
Revises: 7ddfc1ae036c
Create Date: 2021-07-29 23:55:46.655559

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'f52267133dcc'
down_revision = '7ddfc1ae036c'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('groups', sa.Column('follower_count', sa.Integer(), server_default='0', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('groups', 'follower_count')
    # ### end Alembic commands ###
