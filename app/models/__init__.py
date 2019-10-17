from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import FlaskPlugin

make_versioned(plugins=[FlaskPlugin()], options={
    'strategy': 'subquery'
})

db = SQLAlchemy()
