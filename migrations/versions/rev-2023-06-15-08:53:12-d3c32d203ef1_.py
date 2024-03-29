"""empty message
Revision ID: d3c32d203ef1
Revises: 410e54b84481
Create Date: 2023-06-15 08:53:12.741108
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3c32d203ef1'
down_revision = '410e54b84481'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('custom_forms', sa.Column('form_id', sa.String(), nullable=True))
    op.add_column('custom_forms', sa.Column('min', sa.Integer(), nullable=True))
    op.add_column('custom_forms', sa.Column('max', sa.Integer(), nullable=True))
    op.add_column('tickets', sa.Column('form_id', sa.String(), nullable=True))
    op.drop_constraint('custom_form_identifier', 'custom_forms', type_='unique')
    op.create_unique_constraint('custom_form_identifier', 'custom_forms', ['event_id', 'field_identifier', 'form', 'form_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tickets', 'form_id')
    op.drop_column('custom_forms', 'form_id')
    op.drop_column('custom_forms', 'max')
    op.drop_column('custom_forms', 'min')
    op.drop_constraint('custom_form_identifier', 'custom_forms', type_='unique')
    op.create_unique_constraint('custom_form_identifier', 'custom_forms', ['event_id', 'field_identifier', 'form'])
    # ### end Alembic commands ###