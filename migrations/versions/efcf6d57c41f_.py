"""empty message

Revision ID: efcf6d57c41f
Revises: 43e8c59337ae
Create Date: 2019-06-22 16:41:02.180121

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'efcf6d57c41f'
down_revision = '43e8c59337ae'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('speaker', sa.Column('is_email_override', sa.Boolean(), server_default='False', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('speaker', 'is_email_override')
    # ### end Alembic commands ###
