"""lowercase discount code

Revision ID: ba651e8ce9a3
Revises: 4bdb4809f519
Create Date: 2019-05-21 03:16:20.525011

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'ba651e8ce9a3'
down_revision = '4bdb4809f519'


def upgrade():
    op.execute("create extension if not exists citext;", execution_options=None)
    op.execute("alter table discount_codes alter column code type citext;",
               execution_options=None)
    op.create_unique_constraint('uq_event_discount_code', 'discount_codes', ['event_id', 'code'])


def downgrade():
    op.drop_constraint('uq_event_discount_code', 'discount_codes', type_='unique')
    op.execute("alter table discount_codes alter column code type text;",
               execution_options=None)
