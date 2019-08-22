"""Renaming Table from association to ticket_tagging
Revision ID: 90d62fe3b5f4
Revises: 90d62fe3b5e3
Create Date: 2019-08-23 03:35:58.92665
"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


 # revision identifiers, used by Alembic.
 # This is a hand-written migration , Please check thouroughly .
revision = '90d62fe3b5f4'
down_revision = '90d62fe3b5e3'


def upgrade():
	op.rename('ticket_tagging', 'association')


def downgrade():
    op.rename('ticket_tagging', 'association')