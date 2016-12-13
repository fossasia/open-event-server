from app.helpers.data_getter import DataGetter
from app.helpers.helpers import represents_int


def get_sponsors_json(event_id_or_sponsors):

    if represents_int(event_id_or_sponsors):
        sponsors = DataGetter.get_sponsors(event_id_or_sponsors)
    else:
        sponsors = event_id_or_sponsors

    data = []
    for sponsor in sponsors:
        data.append(sponsor.serialize)

    return data


def save_sponsors_from_json(json, event_id=None):
    pass

