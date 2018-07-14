"""empty message

Revision ID: 713af9635f46
Revises: 3a01b7d9d55e
Create Date: 2018-06-27 02:55:35.951641

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '713af9635f46'
down_revision = '3a01b7d9d55e'


def upgrade():
    op.drop_column('discount_codes', 'tickets')
    op.create_table('discount_codes_tickets',
    sa.Column('discount_code_id', sa.Integer(), nullable=False),
    sa.Column('ticket_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(
        ['discount_code_id'], ['discount_codes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(
        ['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('discount_code_id', 'ticket_id')
    )


def downgrade():
    op.add_column('discount_codes', sa.Column(
        'tickets', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_table('discount_codes_tickets')
