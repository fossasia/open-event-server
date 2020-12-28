"""empty message

Revision ID: 7374b18af581
Revises: b0c55c767022
Create Date: 2020-12-28 11:07:56.703331

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '7374b18af581'
down_revision = 'b0c55c767022'


def upgrade():
    op.execute("UPDATE custom_forms SET is_public=True WHERE form='session';")


def downgrade():
    pass
