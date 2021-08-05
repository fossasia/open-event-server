"""empty message

Revision ID: 3389ffd15a1c
Revises: ab0e4baaabab
Create Date: 2021-08-03 16:39:40.084656

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '3389ffd15a1c'
down_revision = 'ab0e4baaabab'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('total_sales', sa.Integer(), nullable=True))
    op.add_column('events_version', sa.Column('total_sales', sa.Integer(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events_version', 'total_sales')
    op.drop_column('events', 'total_sales')
    # ### end Alembic commands ###
