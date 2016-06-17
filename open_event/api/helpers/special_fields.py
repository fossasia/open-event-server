from open_event.helpers.data_getter import DataGetter

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
