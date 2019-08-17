"""duplicate ticket tag

Revision ID: 9172ceb350b8
Revises: cd3beca1951a
Create Date: 2019-08-17 20:46:39.773326

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '9172ceb350b8'
down_revision = '246b5b6123af'


def upgrade():
    op.execute("UPDATE ticket_tag SET deleted_at = current_timestamp, name = concat(name, '.deleted') where name not in (SELECT DISTINCT name FROM (SELECT DISTINCT name, event_id FROM ticket_tag)as name);",
               execution_options=None)


def downgrade():
    op.execute(
        "UPDATE ticket_tag SET deleted_at = null, name = left(name, length(name)-8) where right(name, 8) = '.deleted';",
        execution_options=None)
