"""empty message

Revision ID: 3389ffd15a1c
Revises: f52267133dcc
Create Date: 2021-08-03 16:39:40.084656

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '3389ffd15a1c'
down_revision = 'f52267133dcc'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('rough_sales', sa.Integer(), nullable=True))
    op.add_column('events_version', sa.Column('rough_sales', sa.Integer(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events_version', 'rough_sales')
    op.drop_column('events', 'rough_sales')
    # ### end Alembic commands ###
