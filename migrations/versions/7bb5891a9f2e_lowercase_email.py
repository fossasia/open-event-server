"""lowercase_email

Revision ID: 7bb5891a9f2e
Revises: 6e5c574cbfb8
Create Date: 2019-03-30 12:51:48.134800

"""

from alembic import op
from sqlalchemy import func
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '7bb5891a9f2e'
down_revision = '6e5c574cbfb8'


def upgrade():
    op.execute("UPDATE users SET deleted_at = current_timestamp, _email = concat(_email, '_') where _email not in (SELECT DISTINCT ON (upper(_email)) _email FROM users);",
               execution_options=None)
    op.execute("create extension citext;",
               execution_options=None)
    op.execute("alter table users alter column _email type citext;",
               execution_options=None)


def downgrade():
    op.execute("alter table users alter column _email type text;",
               execution_options=None)
    op.execute("UPDATE users SET deleted_at = null, _email = left(_email, length(_email)-1) where right(_email, 1) = '_';",
               execution_options=None)
    op.execute("drop extension citext;",
               execution_options=None)
