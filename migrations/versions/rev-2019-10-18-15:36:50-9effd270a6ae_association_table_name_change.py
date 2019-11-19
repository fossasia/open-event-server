"""association table name change

Revision ID: 9effd270a6ae
Revises: 7c32ba647a18
Create Date: 2019-10-18 15:36:50.302138

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '9effd270a6ae'
down_revision = '7c32ba647a18'


def upgrade():
    op.rename_table('association', 'ticket_tagging')


def downgrade():
    op.rename_table('ticket_tagging', 'association')
