"""empty message

Revision ID: b08a4ffff5dd
Revises: 43e8c59337ae
Create Date: 2019-06-26 18:20:41.181139

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'b08a4ffff5dd'
down_revision = '43e8c59337ae'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('admin_billing_additional_info', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_billing_address', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_billing_city', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_billing_contact_name', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_billing_country', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_billing_email', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_billing_phone', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_billing_tax_info', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_billing_zip', sa.String(), nullable=True))
    op.add_column('settings', sa.Column('admin_company', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'admin_company')
    op.drop_column('settings', 'admin_billing_zip')
    op.drop_column('settings', 'admin_billing_tax_info')
    op.drop_column('settings', 'admin_billing_phone')
    op.drop_column('settings', 'admin_billing_email')
    op.drop_column('settings', 'admin_billing_country')
    op.drop_column('settings', 'admin_billing_contact_name')
    op.drop_column('settings', 'admin_billing_city')
    op.drop_column('settings', 'admin_billing_address')
    op.drop_column('settings', 'admin_billing_additional_info')
    # ### end Alembic commands ###
