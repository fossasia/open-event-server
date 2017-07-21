"""empty message

Revision ID: 2b39d8c05788
Revises: 8500f5ec6c45
Create Date: 2017-07-17 16:11:47.234638

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2b39d8c05788'
down_revision = 'c5fc44dd6653'

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('frontend_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'frontend_url')
    # ### end Alembic commands ###
