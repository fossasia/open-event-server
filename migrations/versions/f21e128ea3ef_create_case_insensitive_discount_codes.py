"""Create case insensitive discount codes

Revision ID: f21e128ea3ef
Revises: 7bb5891a9f2e
Create Date: 2019-04-18 16:30:17.668956

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'f21e128ea3ef'
down_revision = '7bb5891a9f2e'


def upgrade():
    op.execute("UPDATE discount_codes SET code = concat(code, '_') where code not in (SELECT DISTINCT ON (upper(code)) code FROM discount_codes GROUP BY event_id);",
               execution_options=None)
    op.execute("alter table discount_codes alter column code type citext;",
               execution_options=None)


def downgrade():
    op.execute("alter table discount_codes alter column code type text;",
               execution_options=None)
    op.execute("drop extension citext CASCADE;",
               execution_options=None)