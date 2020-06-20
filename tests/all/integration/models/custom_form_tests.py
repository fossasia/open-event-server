from app.models.custom_form import CustomForms, assign_field_names
from tests.factories.event import EventFactoryBasic


def test_custom_form_name(db):
    event = EventFactoryBasic()
    speaker_custom_form = CustomForms(
        event=event, field_identifier='speakingExperience', form='speaker', type='text'
    )
    attendee_custom_form = CustomForms(
        event=event, field_identifier='taxBusinessInfo', form='attendee', type='text'
    )
    session_custom_form = CustomForms(
        event=event, field_identifier='longAbstract', form='session', type='text'
    )
    db.session.commit()

    assert speaker_custom_form.name == 'Speaking Experience'
    assert attendee_custom_form.name == 'Tax Business Info'
    assert session_custom_form.name == 'Long Abstract'


def test_override_custom_form_name(db):
    event = EventFactoryBasic()
    overridden_custom_form = CustomForms(
        event=event,
        field_identifier='shippingAddress',
        name='Home Address',
        form='attendee',
        type='text',
    )
    custom_custom_form = CustomForms(
        event=event,
        field_identifier='portNumber',
        name='Portable Number',
        form='attendee',
        type='text',
    )
    db.session.commit()

    assert overridden_custom_form.name == 'Shipping Address'
    assert custom_custom_form.name == 'Portable Number'


def test_assigning_old_form_name(db):
    event = EventFactoryBasic()
    speaker_custom_form = CustomForms(
        event=event, field_identifier='speakingExperience', form='speaker', type='text'
    )
    attendee_custom_form = CustomForms(
        event=event, field_identifier='taxBusinessInfo', form='attendee', type='text'
    )
    session_custom_form = CustomForms(
        event=event, field_identifier='longAbstract', form='session', type='text'
    )
    none_custom_form = CustomForms(
        event=event, field_identifier='showNumber', form='attendee', type='text'
    )
    db.session.commit()

    assert speaker_custom_form.name == 'Speaking Experience'
    assert none_custom_form.name is None

    db.session.execute('update custom_forms set name = null')
    db.session.commit()

    db.session.refresh(speaker_custom_form)
    db.session.refresh(attendee_custom_form)
    db.session.refresh(session_custom_form)
    db.session.refresh(none_custom_form)

    assert speaker_custom_form.name is None
    assert attendee_custom_form.name is None
    assert session_custom_form.name is None
    assert none_custom_form.name is None

    assign_field_names(db.session)

    db.session.refresh(speaker_custom_form)
    db.session.refresh(attendee_custom_form)
    db.session.refresh(session_custom_form)
    db.session.refresh(none_custom_form)

    assert speaker_custom_form.name == 'Speaking Experience'
    assert attendee_custom_form.name == 'Tax Business Info'
    assert session_custom_form.name == 'Long Abstract'
    assert none_custom_form.name is None
