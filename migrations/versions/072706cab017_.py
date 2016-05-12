"""empty message

Revision ID: 072706cab017
Revises: None
Create Date: 2016-05-10 05:00:43.419992

"""

# revision identifiers, used by Alembic.
revision = '072706cab017'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('avatar', sa.String(length=500), nullable=True))
    op.add_column('user', sa.Column('tokens', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'tokens')
    op.drop_column('user', 'avatar')
    ### end Alembic commands ###
