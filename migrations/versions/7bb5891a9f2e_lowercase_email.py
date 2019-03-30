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
    op.execute("delete from users where lower(_email) <> _email;",
               execution_options=None)
    op.execute("create unique index users_lower_email on users (lower(_email));",
               execution_options=None)


def downgrade():
    op.execute("drop index users_lower_email;",
               execution_options=None)
