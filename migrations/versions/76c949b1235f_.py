"""The events model and api migrations

Revision ID: 76c949b1235f
Revises: de59ac570231
Create Date: 2017-06-18 23:17:01.159393

"""

# revision identifiers, used by Alembic.
revision = '76c949b1235f'
down_revision = 'de59ac570231'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('events', 'pay_by_stripe', new_column_name='can_pay_by_stripe')
    op.alter_column('events', 'pay_by_bank', new_column_name='can_pay_by_bank')
    op.alter_column('events', 'pay_by_paypal', new_column_name='can_pay_by_paypal')
    op.alter_column('events', 'pay_by_cheque', new_column_name='can_pay_by_cheque')
    op.alter_column('events', 'pay_onsite', new_column_name='can_pay_onsite')
    op.alter_column('events', 'tax_allow', new_column_name='is_tax_enabled')
    op.alter_column('events', 'ticket_include', new_column_name='is_ticketing_enabled')
    op.alter_column('events', 'has_session_speakers', new_column_name='has_sessions_speakers')
    op.alter_column('events', 'sponsors_enabled', new_column_name='is_sponsors_enabled')
    op.drop_column('events', 'email')

    op.alter_column('events_version', 'pay_by_stripe', new_column_name='can_pay_by_stripe')
    op.alter_column('events_version', 'pay_by_bank', new_column_name='can_pay_by_bank')
    op.alter_column('events_version', 'pay_by_paypal', new_column_name='can_pay_by_paypal')
    op.alter_column('events_version', 'pay_by_cheque', new_column_name='can_pay_by_cheque')
    op.alter_column('events_version', 'pay_onsite', new_column_name='can_pay_onsite')
    op.alter_column('events_version', 'tax_allow', new_column_name='is_tax_enabled')
    op.alter_column('events_version', 'ticket_include', new_column_name='is_ticketing_enabled')
    op.alter_column('events_version', 'has_session_speakers',
                    new_column_name='has_sessions_speakers')
    op.alter_column('events_version', 'sponsors_enabled', new_column_name='is_sponsors_enabled')
    op.drop_column('events_version', 'email')

    op.execute('ALTER TABLE events ALTER COLUMN show_map drop default')
    op.execute('ALTER TABLE events ALTER COLUMN show_map TYPE BOOLEAN USING (show_map::boolean)')
    op.execute('ALTER TABLE events ALTER COLUMN show_map SET DEFAULT TRUE')
    op.alter_column('events', 'show_map', new_column_name='is_map_shown')

    op.execute('ALTER TABLE events_version ALTER COLUMN show_map drop default')
    op.execute('ALTER TABLE events_version ALTER COLUMN show_map TYPE BOOLEAN USING (show_map::boolean)')
    op.execute('ALTER TABLE events_version ALTER COLUMN show_map SET DEFAULT TRUE')
    op.alter_column('events_version', 'show_map', new_column_name='is_map_shown')

    op.execute('UPDATE events SET state = LOWER(state)')
    op.execute('UPDATE events_version SET state = LOWER(state)')


def downgrade():
    op.alter_column('events', 'can_pay_by_stripe', new_column_name='pay_by_stripe')
    op.alter_column('events', 'can_pay_by_bank', new_column_name='pay_by_bank')
    op.alter_column('events', 'can_pay_by_cheque', new_column_name='pay_by_cheque')
    op.alter_column('events', 'can_pay_by_paypal', new_column_name='pay_by_paypal')
    op.alter_column('events', 'can_pay_onsite', new_column_name='pay_onsite')
    op.alter_column('events', 'is_tax_enabled', new_column_name='tax_allow')
    op.alter_column('events', 'is_ticketing_enabled', new_column_name='ticket_include')
    op.alter_column('events', 'has_sessions_speakers', new_column_name='has_session_speakers')
    op.alter_column('events', 'is_sponsors_enabled', new_column_name='sponsors_enabled')
    op.add_column('events', sa.Column('email', sa.String(), nullable=True))

    op.alter_column('events_version', 'can_pay_by_stripe', new_column_name='pay_by_stripe')
    op.alter_column('events_version', 'can_pay_by_bank', new_column_name='pay_by_bank')
    op.alter_column('events_version', 'can_pay_by_paypal', new_column_name='pay_by_paypal')
    op.alter_column('events_version', 'can_pay_by_cheque', new_column_name='pay_by_cheque')
    op.alter_column('events_version', 'can_pay_onsite', new_column_name='pay_onsite')
    op.alter_column('events_version', 'has_sessions_speakers',
                    new_column_name='has_session_speakers')
    op.alter_column('events_version', 'is_tax_enabled', new_column_name='tax_allow')
    op.alter_column('events_version', 'is_ticketing_enabled', new_column_name='ticket_include')
    op.alter_column('events_version', 'is_sponsors_enabled', new_column_name='sponsors_enabled')
    op.add_column('events_version', sa.Column('email', sa.String(), nullable=True))

    op.execute('ALTER TABLE events ALTER COLUMN is_map_shown drop default')
    op.execute('ALTER TABLE events ALTER COLUMN is_map_shown TYPE INTEGER USING (is_map_shown::integer)')
    op.execute('ALTER TABLE events ALTER COLUMN is_map_shown SET DEFAULT 1')
    op.alter_column('events', 'is_map_shown', new_column_name='show_map')

    op.execute('ALTER TABLE events_version ALTER COLUMN is_map_shown drop default')
    op.execute(
        'ALTER TABLE events_version ALTER COLUMN is_map_shown TYPE INTEGER USING (is_map_shown::integer)')
    op.execute('ALTER TABLE events_version ALTER COLUMN is_map_shown SET DEFAULT 1')
    op.alter_column('events_version', 'is_map_shown', new_column_name='show_map')

    op.execute('UPDATE events SET state = INITCAP(state)')
    op.execute('UPDATE events_version SET state = INITCAP(state)')
