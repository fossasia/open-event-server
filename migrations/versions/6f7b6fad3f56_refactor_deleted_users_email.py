"""Refactor deleted users email
Revision ID: 6f7b6fad3f56
Revises: 6f7b6fad3f55
Create Date: 2019-05-24 03:26:25
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '6f7b6fad3f56'
down_revision = '6f7b6fad3f55'


def upgrade():
    op.execute("UPDATE users SET _email = concat(_email, '.deleted') where deleted_at IS NOT NULL;",
               execution_options=None)

def downgrade():
    op.execute("UPDATE users SET _email = left(_email, length(_email)-8) where right(_email, 8) = '.deleted' and deleted_at IS NOT NULL;",
               execution_options=None)
