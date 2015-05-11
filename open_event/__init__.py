from flask import Flask, render_template
from open_event.models import db
app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

