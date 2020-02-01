import factory

import app.factories.common as common
from app.models.ticket_holder import TicketHolder, db


class TicketHolderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketHolder
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    firstname = 'John'
    lastname = 'Doe'
    email = common.email_
    address = common.string_
    city = common.string_
    state = common.string_
    country = common.country_
    job_title = common.string_
    phone = common.string_
    billing_address = common.string_
    home_address = common.string_
    shipping_address = common.string_
    company = common.string_
    work_address = common.string_
    work_phone = common.string_
    website = common.url_
    blog = common.url_
    twitter = common.socialUrl_('twitter')
    facebook = common.socialUrl_('facebook')
    github = common.socialUrl_('github')
    age_group = common.string_
    birth_date = common.date_
    pdf_url = common.url_
