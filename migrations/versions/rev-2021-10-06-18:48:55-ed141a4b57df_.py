"""empty message

Revision ID: ed141a4b57df
Revises: 3a14893d21f0
Create Date: 2021-10-06 18:48:55.752566

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'ed141a4b57df'
down_revision = '3a14893d21f0'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('groups', sa.Column('thumbnail_image_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('groups', 'thumbnail_image_url')
    # ### end Alembic commands ###
