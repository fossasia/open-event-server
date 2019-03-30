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
    op.execute(" UPDATE users SET deleted_at = current_timestamp FROM (SELECT lower(_email) FROM users GROUP BY lower(_email) HAVING COUNT(*) > 1) as email where lower(_email) != _email;",
               execution_options=None)


def downgrade():
    pass
