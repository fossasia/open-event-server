"""empty message

Revision ID: 304d6550a1e6
Revises: 8621f70992ba
Create Date: 2019-12-30 01:58:59.917630

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '304d6550a1e6'
down_revision = '8621f70992ba'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ticket_holders', 'event_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('ticket_holders', 'ticket_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ticket_holders', 'ticket_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('ticket_holders', 'event_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
