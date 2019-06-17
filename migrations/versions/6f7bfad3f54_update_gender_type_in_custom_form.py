"""Update gender field in custom form from text to select

Revision ID: 6f7b6fad3f54
Revises: 6f7b6fad3f53
Create Date: 2019-05-17 10:30:57.129985

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '6f7b6fad3f54'
down_revision = '6f7b6fad3f53'


def upgrade():
    op.execute("UPDATE custom_forms SET type = 'select' where field_identifier = 'gender';",
               execution_options=None)
    


def downgrade():
    op.execute("UPDATE custom_forms SET type = 'text' where field_identifier = 'gender';",
               execution_options=None)
