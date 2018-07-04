set -e
python3 create_db.py $ADMIN_EMAIL $ADMIN_PASSWORD
python3 manage.py db stamp head
