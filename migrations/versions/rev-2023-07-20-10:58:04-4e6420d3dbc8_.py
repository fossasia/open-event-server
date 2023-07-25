"""empty message

Revision ID: 4e6420d3dbc8
Revises: 3b784f9c98c7
Create Date: 2023-07-20 10:58:04.278543

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e6420d3dbc8'
down_revision = '3b784f9c98c7'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('station_store_paxs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('station_id', sa.Integer(), nullable=True),
    sa.Column('session_id', sa.Integer(), nullable=True),
    sa.Column('current_pax', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['station_id'], ['station.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('station_store_paxs')
    # ### end Alembic commands ###
