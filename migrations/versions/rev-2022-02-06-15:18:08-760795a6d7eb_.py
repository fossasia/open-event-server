"""empty message

Revision ID: 760795a6d7eb
Revises: b0985248e3d9
Create Date: 2022-02-06 15:18:08.146243

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '760795a6d7eb'
down_revision = 'b0985248e3d9'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('video_streams', sa.Column('bg_img_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('video_streams', 'bg_img_url')
    # ### end Alembic commands ###
