"""Add group.social_links

Revision ID: eecca008e169
Revises: 6b3498cc0457
Create Date: 2021-07-07 03:47:53.181302

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'eecca008e169'
down_revision = '6b3498cc0457'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('groups', sa.Column('social_links', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('groups', 'social_links')
    # ### end Alembic commands ###
