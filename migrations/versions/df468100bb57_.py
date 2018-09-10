"""empty message

Revision ID:
Revises: 82cdc4ac5d20
Create Date: 2018-07-06 20:56:10.803301

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'df468100bb57'
down_revision = '82cdc4ac5d20'


def upgrade():
    op.add_column('ticket_holders', sa.Column(
        'is_checked_out', sa.Boolean(), nullable=True))
    op.add_column('ticket_holders', sa.Column(
        'checkout_times', sa.String(), nullable=True))


def downgrade():
    op.drop_column('ticket_holders', 'is_checked_out')
    op.drop_column('ticket_holders', 'checkout_times')
