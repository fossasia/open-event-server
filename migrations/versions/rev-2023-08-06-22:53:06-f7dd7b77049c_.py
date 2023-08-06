"""empty message

Revision ID: f7dd7b77049c
Revises: 8b5bc48e1d4c
Create Date: 2023-08-06 22:53:06.358005

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7dd7b77049c'
down_revision = '8b5bc48e1d4c'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('access_code_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'orders', 'access_codes', ['access_code_id'], ['id'], ondelete='SET NULL')
    op.add_column('ticket_holders', sa.Column('is_discount_applied', sa.Boolean(), nullable=True))
    op.add_column('ticket_holders', sa.Column('is_access_code_applied', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ticket_holders', 'is_access_code_applied')
    op.drop_column('ticket_holders', 'is_discount_applied')
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.drop_column('orders', 'access_code_id')
    # ### end Alembic commands ###
