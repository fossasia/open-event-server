"""empty message

Revision ID: 7e91153d66b0
Revises: 8b5bcsea1d4c
Create Date: 2023-08-08 15:14:57.455117

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e91153d66b0'
down_revision = '8b5bcsea1d4c'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('session_types', sa.Column('position', sa.Integer(), nullable=True))
    op.add_column('tracks', sa.Column('position', sa.Integer(), nullable=True))
    # ### end Alembic commands ###
    op.execute("UPDATE session_types SET position = 0")
    op.alter_column('session_types', 'position', nullable=False)
    op.execute("UPDATE tracks SET position = 0")
    op.alter_column('tracks', 'position', nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tracks', 'position')
    op.drop_column('session_types', 'position')
    # ### end Alembic commands ###
