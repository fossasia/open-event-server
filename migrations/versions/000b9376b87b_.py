"""empty message

Revision ID: 000b9376b87b
Revises: 6440077182f0
Create Date: 2018-07-05 09:52:56.681093

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '000b9376b87b'
down_revision = '6440077182f0'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event_locations')
    # ### end Alembic commands ###
