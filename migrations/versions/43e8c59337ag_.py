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
    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) VALUES((SELECT id FROM roles WHERE name='owner'), 1, true, true, true, true)")
    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) VALUES((SELECT id FROM roles WHERE name='owner'), 2, true, true, true, true)")
    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) VALUES((SELECT id FROM roles WHERE name='owner'), 3, true, true, true, true)")
    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) VALUES((SELECT id FROM roles WHERE name='owner'), 4, true, true, true, true)")
    op.execute("INSERT INTO permissions(role_id, service_id, can_create, can_read, can_update, can_delete) VALUES((SELECT id FROM roles WHERE name='owner'), 5, true, true, true, true)")



def downgrade():
    op.execute("DELETE FROM permissions WHERE role_id=(SELECT id FROM roles WHERE name='owner')")
