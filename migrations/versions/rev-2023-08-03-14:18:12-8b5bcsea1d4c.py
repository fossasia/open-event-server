"""empty message

Revision ID: 8b5bcsea1d4c
Revises: 8b5bc48e1d4c
Create Date: 2023-08-03 14:18:12.187180

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '8b5bcsea1d4c'
down_revision = '8b5bc48e1d4c'


def upgrade():
    op.execute("insert into video_channels (name, provider, url) values('YouTube Privacy', 'youtube_privacy', 'https://youtube-nocookie.com');")


def downgrade():
    op.execute("delete from video_channels where provider = 'youtube_privacy';")
