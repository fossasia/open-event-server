"""empty message

Revision ID: 2b19596af9f0
Revises: 2d3705de8180
Create Date: 2023-07-18 15:27:36.059991

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b19596af9f0'
down_revision = '2d3705de8180'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ticket_holders', sa.Column('is_badge_printed', sa.Boolean(), nullable=True))
    op.add_column('ticket_holders', sa.Column('badge_printed_at', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('ticket_holders', 'firstname',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('ticket_holders', 'lastname',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ticket_holders', 'lastname',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('ticket_holders', 'firstname',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('ticket_holders', 'badge_printed_at')
    op.drop_column('ticket_holders', 'is_badge_printed')
    # ### end Alembic commands ###
