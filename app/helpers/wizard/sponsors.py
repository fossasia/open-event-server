from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import represents_int
from app.helpers.storage import UPLOAD_PATHS
from app.helpers.wizard.helpers import save_event_image
from app.models import db
from app.models.sponsor import Sponsor


def get_sponsors_json(event_id_or_sponsors):
    if represents_int(event_id_or_sponsors):
        sponsors = DataGetter.get_sponsors(event_id_or_sponsors)
    else:
        sponsors = event_id_or_sponsors

    data = []
    for sponsor in sponsors:
        data.append(sponsor.serialize)
 
    return sorted(data, key=lambda x: x['id'])


def save_sponsors_from_json(json, event_id=None):
    event_id = event_id if event_id else json['event_id']
    event = DataGetter.get_event(event_id)
    sponsors_enabled = json['sponsors_enabled']

    if sponsors_enabled:
        ids = []
        for sponsor in json['sponsors']:
            if sponsor['id'] and represents_int(sponsor['id']):
                item = Sponsor.query.get(sponsor['id'])
            else:
                item = Sponsor(event_id=event_id)

            if sponsor['name'].strip() == '':
                continue

            item.name = sponsor['name']
            item.level = sponsor['level']
            item.sponsor_type = sponsor['type']
            item.url = sponsor['url']
            item.description = sponsor['description']

            save_to_db(item)
            if item.logo != sponsor['logo']:
                if sponsor['logo'] and sponsor['logo'] != '':
                    item.logo = save_event_image(sponsor['logo'], UPLOAD_PATHS['sponsors']['logo'].format(
                        event_id=int(event.id), id=int(item.id)
                    ), remove_after_upload=False)
                else:
                    item.logo = ''

            save_to_db(item)
            ids.append(item.id)

        if len(ids) > 0:
            Sponsor.query.filter(~Sponsor.id.in_(ids)).filter_by(event_id=event_id).delete(synchronize_session='fetch')
    else:
        Sponsor.query.filter_by(event_id=event_id).delete(synchronize_session='fetch')

    event.state = json['state'] if event.location_name.strip() != '' else 'Draft'
    save_to_db(event)
    return {
        'event_id': event.id
    }
