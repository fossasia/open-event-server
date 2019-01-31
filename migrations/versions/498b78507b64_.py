"""empty message

Revision ID: 498b78507b64
Revises: e3caa0f2a16c
Create Date: 2019-01-31 14:35:08.791562

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '498b78507b64'
down_revision = 'e3caa0f2a16c'


def upgrade():
    op.add_column(u'events',sa.Column('is_featured', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column(u'events', 'is_featured')