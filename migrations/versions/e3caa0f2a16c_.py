"""empty message

Revision ID: e3caa0f2a16c
Revises: 41818fe31207
Create Date: 2019-01-30 02:32:10.365941

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3caa0f2a16c'
down_revision = '41818fe31207'


def upgrade():
    op.add_column('users', sa.Column('was_registered_with_order', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column('users', 'was_registered_with_order')
    # ### end Alembic commands ###
