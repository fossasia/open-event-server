"""empty message

Revision ID: 8b5bc48e1d4c
Revises: 21c79d253f21
Create Date: 2023-08-01 14:10:12.187180

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8b5bc48e1d4c'
down_revision = '21c79d253f21'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('badge_field_forms', 'font_weight',
               existing_type=sa.Integer(),
               type_=postgresql.ARRAY(sa.JSON()),
               postgresql_using='font_weight::text::json[]',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('badge_field_forms', 'font_weight',
               existing_type=postgresql.ARRAY(sa.JSON()),
               type_=sa.Integer(),
                    postgresql_using='font_weight::text::integer',
               existing_nullable=True)
    # ### end Alembic commands ###
