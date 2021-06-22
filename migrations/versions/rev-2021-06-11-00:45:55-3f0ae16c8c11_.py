"""empty message

Revision ID: 3f0ae16c8c11
Revises: 4a453095d93e
Create Date: 2021-06-11 00:45:55.279136

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '3f0ae16c8c11'
down_revision = '4a453095d93e'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('is_videoroom_enabled', sa.Boolean(), nullable=False, server_default='False'))
    op.add_column('events_version', sa.Column('is_videoroom_enabled', sa.Boolean(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events_version', 'is_videoroom_enabled')
    op.drop_column('events', 'is_videoroom_enabled')
    # ### end Alembic commands ###
