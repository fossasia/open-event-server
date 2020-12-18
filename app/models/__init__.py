import sys

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import FlaskPlugin

make_versioned(plugins=[FlaskPlugin()], options={'strategy': 'subquery'})

db = SQLAlchemy()

# Proxy session if we are testing to point session
# to a nested transaction which is rolled backed
# after each test
if 'pytest' in sys.modules:
    from objproxies import CallbackProxy

    db._session = db.session
    db.session = CallbackProxy(lambda: db._session)
