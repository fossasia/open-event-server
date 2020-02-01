import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.factories.microlocation import MicrolocationFactory
from app.factories.session_type import SessionTypeFactory
from app.factories.track import TrackFactory
from app.models.session import Session, db


class SessionFactoryBase(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Session
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    title = common.string_
    subtitle = common.string_
    level = common.int_
    short_abstract = common.string_
    long_abstract = common.string_ + common.string_
    comments = common.string_
    starts_at = common.dateFuture_
    ends_at = common.dateEndFuture_
    language = "English"
    slides_url = common.url_
    video_url = common.url_
    audio_url = common.url_
    signup_url = common.url_
    state = "accepted"
    submitted_at = common.date_
    is_mail_sent = True


class SessionFactory(SessionFactoryBase):

    event = factory.RelatedFactory(EventFactoryBasic)
    session_type = factory.RelatedFactory(SessionTypeFactory)
    track = factory.RelatedFactory(TrackFactory)
    microlocation = factory.RelatedFactory(MicrolocationFactory)
