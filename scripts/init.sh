set -e
flask create_db $ADMIN_EMAIL $ADMIN_PASSWORD
flask db stamp head
