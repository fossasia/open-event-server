"""empty message

Revision ID: 157df65ec235
Revises: 6b9d98ec9046
Create Date: 2021-02-10 18:44:50.893197

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '157df65ec235'
down_revision = '6b9d98ec9046'


def upgrade():
    op.execute("insert into video_channels (name, provider, url, api_url) values('YouTube', 'youtube', 'https://youtube.com', 'https://www.googleapis.com/youtube/v3');")
    op.execute("update video_streams set channel_id=(select id from video_channels where provider = 'youtube') where url like 'https://youtube.com/%';")
    op.execute("insert into video_channels (name, provider, url, api_url) values('Vimeo', 'vimeo', 'https://vimeo.com', 'https://api.vimeo.com');")
    op.execute("update video_streams set channel_id=(select id from video_channels where provider = 'vimeo') where url like 'https://vimeo.com/%';")


def downgrade():
    op.execute("update video_streams set channel_id=null where url like 'https://youtube.com/%';")
    op.execute("delete from video_channels where provider = 'youtube';")
    op.execute("update video_streams set channel_id=null where url like 'https://vimeo.com/%';")
    op.execute("delete from video_channels where provider = 'vimeo';")
