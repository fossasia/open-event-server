from app.helpers.data_getter import DataGetter

import custom_fields as fields


class EventTypeField(fields.ChoiceString):
    __schema_example__ = DataGetter.get_event_types()[0]

    def __init__(self, **kwargs):
        super(EventTypeField, self).__init__(
            choice_list=DataGetter.get_event_types(),
            **kwargs)


class EventTopicField(fields.ChoiceString):
    __schema_example__ = DataGetter.get_event_topics()[0]

    def __init__(self, **kwargs):
        super(EventTopicField, self).__init__(
            choice_list=DataGetter.get_event_topics(),
            **kwargs)


class EventSubTopicField(fields.ChoiceString):
    __schema_example__ = DataGetter.get_event_subtopics()[
        DataGetter.get_event_topics()[0]
    ][0]

    def __init__(self, **kwargs):
        super(EventSubTopicField, self).__init__(
            choice_list=[],
            **kwargs)

    def validate(self, value):
        topic = self.payload.get('topic')
        if not topic:
            self.choice_list = []
        else:
            self.choice_list = DataGetter.get_event_subtopics().get(topic, [])
        return super(EventSubTopicField, self).validate(value)


class EventPrivacyField(fields.ChoiceString):
    __schema_example__ = 'public'

    def __init__(self, **kwargs):
        super(EventPrivacyField, self).__init__(
            choice_list=['public', 'private'],
            **kwargs
        )


class EventStateField(fields.ChoiceString):
    __schema_example__ = 'Draft'

    def __init__(self, **kwargs):
        super(EventStateField, self).__init__(
            choice_list=['Draft', 'Published', 'Completed', 'Call for papers'],
            **kwargs
        )


class SessionLanguageField(fields.ChoiceString):
    __schema_example__ = DataGetter.get_language_list()[51]

    def __init__(self, **kwargs):
        super(SessionLanguageField, self).__init__(
            choice_list=DataGetter.get_language_list(),
            **kwargs)


class SessionStateField(fields.ChoiceString):
    __schema_example__ = 'pending'

    def __init__(self, **kwargs):
        super(SessionStateField, self).__init__(
            choice_list=['pending', 'accepted', 'rejected'],
            **kwargs)
