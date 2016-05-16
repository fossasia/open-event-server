from ..helpers.data_getter import DataGetter


def event_status_code(event_id):
    """
    Helper function to return status code 200 if event exists
    else 404
    """
    return 200 if DataGetter.get_event(event_id) else 404
