"""insert after_event setting for speaker

Revision ID: de295fee375b
Revises: 0223c881d135
Create Date: 2019-12-09 00:14:14.221105

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'de295fee375b'
down_revision = '0223c881d135'


def upgrade():
    op.execute('INSERT into message_settings (action,mail_status,notification_status,user_control_status) VALUES '
               '(\'After Event to Speaker\', true, true, true )')

def downgrade():
    op.execute('DELETE from message_settings where action=\'After Event to Speaker\' ')
