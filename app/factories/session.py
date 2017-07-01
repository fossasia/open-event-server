import factory
from app.models.session import db, Session
import app.factories.common as common
from app.factories.event import EventFactoryBasic


class SessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Session
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    title = common.string_
    subtitle = common.string_
    level = common.int_
    short_abstract = common.string_
    long_abstract = (common.string_ + common.string_)
    comments = common.string_
    starts_at = common.date_
    ends_at = common.dateEnd_
    language = "English"
    slides_url = common.url_
    video_url = common.url_
    audio_url = common.url_
    signup_url = common.url_
    state = "accepted"
    created_at = common.date_
    submitted_at = common.date_
    is_mail_sent = True
