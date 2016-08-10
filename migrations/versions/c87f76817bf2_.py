"""empty message

Revision ID: c87f76817bf2
Revises: 86fe7df8dca6
Create Date: 2016-08-08 21:57:43.919000

"""

# revision identifiers, used by Alembic.
revision = 'c87f76817bf2'
down_revision = '86fe7df8dca6'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.drop_column('events', 'event_url')
    op.drop_column('events_version', 'event_url')
    pass


def downgrade():
    op.add_column('events', sa.Column('event_url', sa.String(), nullable=True))
    op.add_column('events_version', sa.Column('event_url', sa.String(), nullable=True))
    pass
