from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config


def get_session_from_config():
    """Create a postgres session using the application config"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    maker = sessionmaker()
    maker.configure(bind=engine)

    return maker()
