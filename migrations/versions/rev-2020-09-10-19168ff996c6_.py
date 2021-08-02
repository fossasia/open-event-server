"""empty message

Revision ID: 19168ff996c6
Revises: 3548da69bdec
Create Date: 2020-09-10 19:22:53.695773

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '19168ff996c6'
down_revision = '3548da69bdec'


def upgrade():
    op.execute("UPDATE events SET refund_policy = NULL;", execution_options=None)

def downgrade():
    op.execute("UPDATE events SET refund_policy = 'All sales are final. No refunds shall be issued in any case.' where refund_policy = NULL;", execution_options=None)