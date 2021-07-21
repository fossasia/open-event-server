import json

from app.instance import current_app
from app.models import db


def db_migrate_speaker_doc(db):

    # migrating slides url from url type to JSON type

    conn = db.engine.connect()
    cursor = conn.execute("SELECT * from sessions")
    dict = []
    for row in cursor:
        dict.append({'name': row['title'], 'link': row['slides_url']})
        data = f"'{json.dumps(dict)}'"
        id = row['id']
        conn.execute(f'UPDATE sessions SET slides = {data} WHERE id = {id}')


if __name__ == "__main__":
    with current_app.app_context():
        db_migrate_speaker_doc(db)
