"""lowercase discount code

Revision ID: ba651e8ce9a3
Revises: 6f7b6fad3f55
Create Date: 2019-05-21 03:16:20.525011

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'ba651e8ce9a3'
down_revision = '6f7b6fad3f55'


def upgrade():
    op.execute("UPDATE discount_codes SET code = concat(code, '_') where code not in (SELECT DISTINCT ON (upper(code)) code FROM discount_codes group by event_id, code);",
               execution_options=None)
    op.execute("alter table discount_codes alter column code type citext;",
               execution_options=None)
    op.execute("alter table discount_codes add constraint uq_discount_codes unique(event_id, code);",
               execution_options=None)


def downgrade():
    op.execute("UPDATE discount_codes SET code = left(code, length(code)-1) where right(code, 1) = '_';",
               execution_options=None)
    op.execute("alter table discount_codes alter column code type text;",
               execution_options=None)
    op.execute("alter table discount_codes drop constraint uq_discount_codes;",
               execution_options=None)
