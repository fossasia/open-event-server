import factory

from app.models.session import Session
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationFactory
from tests.factories.session_type import SessionTypeFactory
from tests.factories.track import TrackFactory, TrackSubFactory


class SessionFactoryBase(BaseFactory):
    class Meta:
        model = Session

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


class SessionSubFactory(SessionFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)
    track = factory.SubFactory(TrackSubFactory)


class SessionFactoryBasic(SessionFactoryBase):
    event_id = 1
    session_type_id = 1
    track_id = 1
    microlocation_id = 1


class SessionFactory(SessionFactoryBasic):
    event = factory.RelatedFactory(EventFactoryBasic)
    session_type = factory.RelatedFactory(SessionTypeFactory)
    track = factory.RelatedFactory(TrackFactory)
    microlocation = factory.RelatedFactory(MicrolocationFactory)
