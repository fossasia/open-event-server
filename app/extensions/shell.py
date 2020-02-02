from app.models import db
from app.models.event import Event
from app.models.order import Order
from app.models.session import Session
from app.models.setting import Setting
from app.models.speaker import Speaker
from app.models.ticket import Ticket
from app.models.track import Track
from app.models.user import User


def init_app(app):
    @app.shell_context_processor
    def shell_context():
        return dict(
            db=db,
            Event=Event,
            Session=Session,
            Ticket=Ticket,
            Order=Order,
            Setting=Setting,
            Speaker=Speaker,
            Track=Track,
            User=User,
        )
