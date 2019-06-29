"""Changing field type of gender from `Text` to `Select`

Revision ID: 43e8c59337af
Revises: b08a4ffff5dd
Create Date: 2019-06-27 20:31:58.92665

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


 # revision identifiers, used by Alembic.
revision = '43e8c59337af'
down_revision = 'b08a4ffff5dd'


def upgrade():
    op.execute("UPDATE custom_forms SET type = 'select' where field_identifier = 'gender';", execution_options=None)



def downgrade():
    op.execute("UPDATE custom_forms SET type = 'text' where field_identifier = 'gender';", execution_options=None)
