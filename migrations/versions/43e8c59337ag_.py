"""Adding permissions for owner

Revision ID: 43e8c59337ag
Revises: 43e8c59337af
Create Date: 2019-07-03 13:21:58.92665

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


 # revision identifiers, used by Alembic.
revision = '43e8c59337ag'
down_revision = '43e8c59337af'


def upgrade():
    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) \
                VALUES((SELECT id FROM roles WHERE name='owner'), (SELECT id from services where name='track'), \
                true, true, true, true)", execution_options=None)

    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) \
                VALUES((SELECT id FROM roles WHERE name='owner'), (SELECT id from services where name='session'), \
                true, true, true, true)", execution_options=None)

    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) \
                VALUES((SELECT id FROM roles WHERE name='owner'), (SELECT id from services where name='speaker'), \
                true, true, true, true)", execution_options=None)

    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) \
                VALUES((SELECT id FROM roles WHERE name='owner'), (SELECT id from services where name='sponsor'), \
                true, true, true, true)", execution_options=None)

    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) \
                VALUES((SELECT id FROM roles WHERE name='owner'), (SELECT id from services where name='microlocation'), \
                true, true, true, true)", execution_options=None)



def downgrade():
    op.execute("DELETE FROM permissions WHERE role_id=(SELECT id FROM roles WHERE name='owner')")
