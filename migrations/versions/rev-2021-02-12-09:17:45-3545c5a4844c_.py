"""empty message

Revision ID: 3545c5a4844c
Revises: 9756adf77900
Create Date: 2021-02-12 09:17:45.265278

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '3545c5a4844c'
down_revision = '9756adf77900'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('is_cfs_enabled', sa.Boolean(), nullable=False, server_default='False'))
    op.add_column('events_version', sa.Column('is_cfs_enabled', sa.Boolean(), autoincrement=False, nullable=True))
    op.execute("UPDATE events SET is_cfs_enabled = True FROM speakers_calls WHERE events.id = speakers_calls.event_id  AND speakers_calls.announcement IS NOT NULL;")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('events_version', 'is_cfs_enabled')
    op.drop_column('events', 'is_cfs_enabled')
    # ### end Alembic commands ###