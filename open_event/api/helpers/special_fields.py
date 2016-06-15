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
