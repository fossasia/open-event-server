"""empty message

Revision ID: eef7c9bc83a0
Revises: dee1ad7bee53
Create Date: 2020-01-13 22:43:30.603812

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'eef7c9bc83a0'
down_revision = 'dee1ad7bee53'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('speaker', sa.Column('instagram', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('speaker', 'instagram')
    # ### end Alembic commands ###
