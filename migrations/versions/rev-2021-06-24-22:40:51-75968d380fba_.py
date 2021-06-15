"""empty message

Revision ID: 75968d380fba
Revises: 6b3498cc0457
Create Date: 2021-06-24 22:40:51.513401

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '75968d380fba'
down_revision = '6b3498cc0457'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('speaker_invites',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('speaker_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['speaker_id'], ['speaker.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email', 'session_id', 'event_id', name='email_session_event_uc')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('speaker_invites')
    # ### end Alembic commands ###
