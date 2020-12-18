"""empty message

Revision ID: f6bd6bce0205
Revises: 295e44c2202b
Create Date: 2020-12-10 05:21:29.855771

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'f6bd6bce0205'
down_revision = '295e44c2202b'


def upgrade():
    op.execute("insert into video_channels (name, provider, url, api_url) values('Jitsi Meet', 'jitsi', 'https://meet.jit.si', 'https://api.jitsi.net');")
    op.execute("update video_streams set channel_id=(select id from video_channels where provider = 'jitsi') where url like 'https://meet.jit.si/%';")


def downgrade():
    op.execute("update video_streams set channel_id=null where url like 'https://meet.jit.si/%';")
    op.execute("delete from video_channels where provider = 'jitsi';")
