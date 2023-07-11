"""empty message

Revision ID: f508644acbd3
Revises: 05b1aab46b66
Create Date: 2023-06-29 15:22:56.735800

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = 'f508644acbd3'
down_revision = '05b1aab46b66'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ticket_holders', 'language_form_1', new_column_name='native_language')
    op.alter_column('ticket_holders', 'language_form_2', new_column_name='fluent_language')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ticket_holders', 'native_language', new_column_name='language_form_1')
    op.alter_column('ticket_holders', 'fluent_language', new_column_name='language_form_2')
    # ### end Alembic commands ###
