"""Changing field type of country from `Text` to `Select`
Revision ID: eef7c9bc83a12
Revises: eef7c9bc83a0
Create Date: 2020-01-16 13:31:58.92665
"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


 # revision identifiers, used by Alembic.
revision = 'eef7c9bc83a12'
down_revision = 'eef7c9bc83a0'


def upgrade():
    op.execute("UPDATE custom_forms SET type = 'select' where field_identifier = 'country' and form = 'attendee';", execution_options=None)



def downgrade():
    op.execute("UPDATE custom_forms SET type = 'text' where field_identifier = 'country' and form = 'attendee';", execution_options=None)
