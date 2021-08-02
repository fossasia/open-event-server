from tests.factories.session import SessionSubFactory


def test_session_site_link(db):
    session = SessionSubFactory(event__identifier='abcde', id=34567)
    db.session.commit()

    assert session.event.site_link == 'http://eventyay.com/e/abcde'
    assert session.site_link == 'http://eventyay.com/e/abcde/session/34567'
