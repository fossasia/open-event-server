"""empty message

Revision ID: 4e61d4df3516
Revises: 2d0760003a8a
Create Date: 2021-01-05 20:43:13.954274

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '4e61d4df3516'
down_revision = '2d0760003a8a'


def upgrade():
    op.execute("DELETE FROM roles WHERE name = 'attendee'")


def downgrade():
    pass
