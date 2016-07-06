"""empty message

Revision ID: 74e76a7976fb
Revises: 5d35fa753afa
Create Date: 2016-06-29 10:34:43.101394

"""

# revision identifiers, used by Alembic.
revision = '74e76a7976fb'
down_revision = '5d35fa753afa'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    op.add_column('session', sa.Column('in_trash', sa.Boolean(), default=False))
    op.add_column('user', sa.Column('in_trash', sa.Boolean(), default=False))
    op.add_column('events', sa.Column('in_trash', sa.Boolean(), default=False))

def downgrade():
	op.drop_column('events', 'in_trash')
	op.drop_column('user', 'in_trash')
	op.drop_column('session', 'in_trash')
