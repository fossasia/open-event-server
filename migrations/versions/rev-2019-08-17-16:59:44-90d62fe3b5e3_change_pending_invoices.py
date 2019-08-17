"""change pending invoices

Revision ID: 90d62fe3b5e3
Revises: cd3beca1951a
Create Date: 2019-08-17 16:59:44.044872

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '90d62fe3b5e3'
down_revision = 'cd3beca1951a'


def upgrade():
	op.execute("UPDATE event_invoices SET status = 'due' where status = 'pending';",
               execution_options=None)


def downgrade():
    op.execute("UPDATE event_invoices SET status = 'pending' where status = 'due';",
               execution_options=None)
