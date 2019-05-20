"""Refactor custom form identifiers
Revision ID: 6f7b6fad3f55
Revises: 6f7b6fad3f54
Create Date: 2019-05-21 01:48:12.345
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '6f7b6fad3f55'
down_revision = '6f7b6fad3f54'


def upgrade():
    op.execute("UPDATE custom_forms SET type = 'select' where field_identifier = 'track';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET type = 'select' where field_identifier = 'sessionType';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET type = 'image' where field_identifier = 'photoUrl';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET field_identifier = 'slidesUrl' where field_identifier = 'slides';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET field_identifier = 'audioUrl' where field_identifier = 'audio';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET field_identifier = 'videoUrl' where field_identifier = 'video';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET field_identifier = 'photoUrl' where field_identifier = 'photo';",
               execution_options=None)


def downgrade():
    op.execute("UPDATE custom_forms SET type = 'text' where field_identifier = 'track';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET type = 'text' where field_identifier = 'sessionType';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET type = 'text' where field_identifier = 'photoUrl';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET field_identifier = 'slides' where field_identifier = 'slidesUrl';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET field_identifier = 'audio' where field_identifier = 'audioUrl';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET field_identifier = 'video' where field_identifier = 'videoUrl';",
               execution_options=None)
    op.execute("UPDATE custom_forms SET field_identifier = 'photo' where field_identifier = 'photoUrl';",
               execution_options=None)
