import json

from sqlalchemy.event import listens_for
from sqlalchemy.schema import UniqueConstraint

from app.api.helpers.utilities import to_snake_case
from app.models import db

SESSION_FORM = {
    "title": {"include": 1, "require": 1},
    "subtitle": {"include": 0, "require": 0},
    "short_abstract": {"include": 1, "require": 0},
    "long_abstract": {"include": 0, "require": 0},
    "comments": {"include": 1, "require": 0},
    "track": {"include": 0, "require": 0},
    "session_type": {"include": 0, "require": 0},
    "language": {"include": 0, "require": 0},
    "slides": {"include": 1, "require": 0},
    "video": {"include": 0, "require": 0},
    "audio": {"include": 0, "require": 0},
}

SPEAKER_FORM = {
    "name": {"include": 1, "require": 1},
    "email": {"include": 1, "require": 1},
    "photo": {"include": 1, "require": 0},
    "organisation": {"include": 1, "require": 0},
    "position": {"include": 1, "require": 0},
    "country": {"include": 1, "require": 0},
    "short_biography": {"include": 1, "require": 0},
    "long_biography": {"include": 0, "require": 0},
    "mobile": {"include": 0, "require": 0},
    "website": {"include": 1, "require": 0},
    "facebook": {"include": 0, "require": 0},
    "twitter": {"include": 1, "require": 0},
    "github": {"include": 0, "require": 0},
    "linkedin": {"include": 0, "require": 0},
}

ATTENDEE_FORM = {
    "firstname": {"include": 1, "require": 1},
    "lastname": {"include": 1, "require": 1},
    "email": {"include": 1, "require": 1},
    "address": {"include": 1, "require": 0},
    "city": {"include": 1, "require": 0},
    "state": {"include": 1, "require": 0},
    "country": {"include": 1, "require": 0},
    "job_title": {"include": 1, "require": 0},
    "phone": {"include": 1, "require": 0},
    "tax_business_info": {"include": 1, "require": 0},
    "billing_address": {"include": 0, "require": 0},
    "home_address": {"include": 0, "require": 0},
    "shipping_address": {"include": 0, "require": 0},
    "company": {"include": 1, "require": 0},
    "work_address": {"include": 0, "require": 0},
    "work_phone": {"include": 0, "require": 0},
    "website": {"include": 1, "require": 0},
    "blog": {"include": 0, "require": 0},
    "twitter": {"include": 1, "require": 0},
    "facebook": {"include": 0, "require": 0},
    "github": {"include": 1, "require": 0},
    "gender": {"include": 0, "require": 0},
    "age_group": {"include": 0, "require": 0},
    "accept_video_recording": {"include": 0, "require": 0},
}

session_form_str = json.dumps(SESSION_FORM, separators=(',', ':'))
speaker_form_str = json.dumps(SPEAKER_FORM, separators=(',', ':'))
attendee_form_str = json.dumps(ATTENDEE_FORM, separators=(',', ':'))


CUSTOM_FORM_IDENTIFIER_NAME_MAP = {
    "session": {
        "title": "Title",
        "subtitle": "Subtitle",
        "shortAbstract": "Short Abstract",
        "longAbstract": "Long Abstract",
        "comments": "Comment",
        "track": "Track",
        "sessionType": "Session Type",
        "level": "Level",
        "language": "Language",
        "slidesUrl": "Slide",
        "slides": "Slides",
        "videoUrl": "Video",
        "audioUrl": "Audio",
        "website": "Website",
        "facebook": "Facebook",
        "twitter": "Twitter",
        "github": "GitHub",
        "linkedin": "Linkedin",
        "instagram": "Instagram",
        "gitlab": "Gitlab",
        "mastodon": "Mastodon",
    },
    "speaker": {
        "name": "Name",
        "email": "Email",
        "photoUrl": "Photo",
        "organisation": "Organisation",
        "position": "Position",
        "address": "Address",
        "country": "Country",
        "city": "City",
        "longBiography": "Long Biography",
        "shortBiography": "Short Biography",
        "speakingExperience": "Speaking Experience",
        "sponsorshipRequired": "Sponsorship Required",
        "gender": "Gender",
        "heardFrom": "Heard From",
        "mobile": "Mobile",
        "website": "Website",
        "facebook": "Facebook",
        "twitter": "Twitter",
        "github": "GitHub",
        "linkedin": "Linkedin",
        "instagram": "Instagram",
        "mastodon": "Mastodon",
    },
    "attendee": {
        "firstname": "First Name",
        "lastname": "Last Name",
        "email": "Email",
        "address": "Address",
        "city": "City",
        "state": "State",
        "country": "Country",
        "jobTitle": "Job Title",
        "phone": "Phone",
        "taxBusinessInfo": "Tax Business Info",
        "billingAddress": "Billing Address",
        "homeAddress": "Home Address",
        "shippingAddress": "Shipping Address",
        "company": "Organisation",
        "workAddress": "Work Address",
        "workPhone": "Work Phone",
        "website": "Website",
        "blog": "Blog",
        "twitter": "Twitter",
        "facebook": "Facebook",
        "github": "GitHub",
        "linkedin": "LinkedIn",
        "instagram": "Instagram",
        "gender": "Gender",
        "ageGroup": "Age Group",
        "acceptVideoRecording": "Photo & video & text consent",
        "acceptShareDetails": "Partner contact consent",
        "acceptReceiveEmails": "Email consent",
    },
}


class CustomForms(db.Model):
    """custom form model class"""

    class TYPE:
        ATTENDEE = 'attendee'
        SESSION = 'session'
        SPEAKER = 'speaker'

    __tablename__ = 'custom_forms'
    __table_args__ = (
        UniqueConstraint(
            'event_id', 'field_identifier', 'form', name='custom_form_identifier'
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    field_identifier = db.Column(db.String, nullable=False)
    form = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    is_required = db.Column(db.Boolean, default=False)
    is_included = db.Column(db.Boolean, default=False)
    is_fixed = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0, nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    is_complex = db.Column(db.Boolean, nullable=False, default=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'))
    custom_form_options = db.relationship('CustomFormOptions', backref="custom_form")

    @property
    def identifier(self):
        return to_snake_case(self.field_identifier)

    def __repr__(self):
        return f'<CustomForm {self.id!r} {self.identifier!r}>'


def get_set_field_name(target: CustomForms) -> str:
    form_map = CUSTOM_FORM_IDENTIFIER_NAME_MAP[target.form]
    target_name = form_map.get(target.field_identifier)
    if target_name:
        target.name = target_name

    return target.name


@listens_for(CustomForms, 'before_insert')
@listens_for(CustomForms, 'before_update')
def generate_name(mapper, connect, target: CustomForms) -> None:
    get_set_field_name(target)


def assign_field_names(session) -> None:
    "Used to migrate existing form fields in DB. Don't modify"
    statements = []

    for form, dict_map in CUSTOM_FORM_IDENTIFIER_NAME_MAP.items():
        for identifier, name in dict_map.items():
            statements.append(
                f"UPDATE custom_forms SET name = '{name}' WHERE form = '{form}' and field_identifier = '{identifier}';"
            )

    for statement in statements:
        session.execute(statement)
