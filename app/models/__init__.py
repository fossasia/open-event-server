from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import FlaskPlugin

# To import all models automatically when someone types `from app.models import *`
from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

make_versioned(plugins=[FlaskPlugin()], options={
    'strategy': 'subquery'
})

db = SQLAlchemy()
