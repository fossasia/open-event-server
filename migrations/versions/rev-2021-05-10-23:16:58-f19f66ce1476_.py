"""empty message

Revision ID: f19f66ce1476
Revises: 51ad369b558b
Create Date: 2021-05-10 23:16:58.818330

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f19f66ce1476'
down_revision = '51ad369b558b'


def upgrade():
    op.execute("UPDATE custom_forms SET type='select' WHERE field_identifier='level';")

def downgrade():
    op.execute("UPDATE custom_forms SET type='text' WHERE field_identifier='level';")
