"""Event model rename has_sessions_speakers to is_sessions_speakers_enabled

Revision ID: da5c6c740257
Revises: 76c949b1235f
Create Date: 2017-06-21 17:31:33.777839

"""

# revision identifiers, used by Alembic.
revision = 'da5c6c740257'
down_revision = '76c949b1235f'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    op.alter_column('events', 'has_sessions_speakers', new_column_name='is_sessions_speakers_enabled')
    op.alter_column('events_version', 'has_sessions_speakers', new_column_name='is_sessions_speakers_enabled')


def downgrade():
    op.alter_column('events', 'is_sessions_speakers_enabled', new_column_name='has_sessions_speakers')
    op.alter_column('events_version', 'is_sessions_speakers_enabled', new_column_name='has_sessions_speakers')


