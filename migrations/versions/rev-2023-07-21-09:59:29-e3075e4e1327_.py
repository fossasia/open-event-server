"""empty message

Revision ID: e3075e4e1327
Revises: 9881f067213b
Create Date: 2023-07-21 09:59:29.133119

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e3075e4e1327'
down_revision = '3b784f9c98c7'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_check_in',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticket_holder_id', sa.Integer(), nullable=True),
    sa.Column('session_id', sa.Integer(), nullable=True),
    sa.Column('station_id', sa.Integer(), nullable=True),
    sa.Column('track_name', sa.String(), nullable=True),
    sa.Column('session_name', sa.String(), nullable=True),
    sa.Column('speaker_name', sa.String(), nullable=True),
    sa.Column('check_in_out_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['station_id'], ['station.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ticket_holder_id'], ['ticket_holders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_check_in')
    # ### end Alembic commands ###