"""empty message

Revision ID: 5c9703d41aa5
Revises: 41818fe31207
Create Date: 2019-01-28 02:57:17.791277

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c9703d41aa5'
down_revision = '41818fe31207'


def upgrade():
    op.add_column(u'events',sa.Column('is_featured', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column(u'events', 'is_featured')
