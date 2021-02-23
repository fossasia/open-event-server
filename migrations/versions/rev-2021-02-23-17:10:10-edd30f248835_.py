"""empty message

Revision ID: edd30f248835
Revises: 0efe87a56e46
Create Date: 2021-02-23 17:10:10.100796

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'edd30f248835'
down_revision = '0efe87a56e46'


def upgrade():
    op.execute("UPDATE video_streams SET extra='{\"autoplay\": false}'");


def downgrade():
	op.execute("UPDATE video_streams SET extra=null");
    
