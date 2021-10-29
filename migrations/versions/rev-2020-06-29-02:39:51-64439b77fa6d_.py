"""empty message

Revision ID: 64439b77fa6d
Revises: abc8b96ce72c
Create Date: 2020-06-29 02:39:51.364914

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '64439b77fa6d'
down_revision = 'abc8b96ce72c'


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