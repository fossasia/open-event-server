import json

import flask_login
from flask import flash
from open_event.api import api
from flask_admin import BaseView, expose

from open_event.views.admin.models_views.events import is_verified_user
from ....helpers.data_getter import DataGetter

class EventApiView(BaseView):

    @expose('/')
    @flask_login.login_required
    def display_api_view(self, event_id):
        event = DataGetter.get_event(event_id)
        data = json.loads(json.dumps(api.__schema__))  # Yep. What you're seeing was intentional.
        events_data = {}
        paths = []
        ctr = 0
        for path in data['paths']:
            if path.startswith('/events/{event_id}'):
                path_modified = path.replace('{event_id}', str(event_id))
                paths.append(path_modified)
                events_data[path_modified] = data['paths'][path]
                events_data[path_modified]['id'] = ctr
                ctr += 1
                for method in data['paths'][path]:
                    if method == "get":
                        try:
                            definition = data['paths'][path][method]['responses']['200']['schema']['items']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['200']['schema']['items']['ref_def'] = data['definitions'][definition]
                        except:
                            pass

                        try:
                            definition = data['paths'][path][method]['responses']['200']['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['200']['schema']['ref_def'] = data['definitions'][definition]
                            for prop in data['definitions'][definition]['properties']:
                                if '$ref' in data['definitions'][definition]['properties'][prop]:
                                    def_ = data['definitions'][definition]['properties'][prop]['$ref'].replace('#/definitions/', '')
                                    events_data[path_modified][method]['responses']['200']['schema']['ref_def']['properties'][prop]['ref_def'] = data['definitions'][def_]
                        except:
                            pass

                        try:
                            definition = data['paths'][path][method]['responses']['400']['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['400']['schema']['ref_def'] = data['definitions'][definition]
                        except:
                            pass

                        try:
                            definition = data['paths'][path][method]['responses']['401']['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['401']['schema']['ref_def'] = data['definitions'][definition]
                        except:
                            pass

                        try:
                            definition = data['paths'][path][method]['responses']['404']['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['404']['schema']['ref_def'] = data['definitions'][definition]
                        except:
                            pass

                    elif method == "post" or method == "put" or method == "delete":
                        try:
                            definition = data['paths'][path][method]['parameters'][0]['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['parameters'][0]['schema']['ref_def'] = data['definitions'][definition]
                            for prop in data['definitions'][definition]['properties']:
                                if '$ref' in data['definitions'][definition]['properties'][prop]:
                                    def_ = data['definitions'][definition]['properties'][prop]['$ref'].replace('#/definitions/', '')
                                    events_data[path_modified][method]['parameters'][0]['schema']['ref_def']['properties'][prop]['ref_def'] = data['definitions'][def_]
                        except:
                            pass

                        try:
                            definition = data['paths'][path][method]['responses']['200']['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['200']['schema']['ref_def'] = data['definitions'][definition]
                            for prop in data['definitions'][definition]['properties']:
                                if '$ref' in data['definitions'][definition]['properties'][prop]:
                                    def_ = data['definitions'][definition]['properties'][prop]['$ref'].replace('#/definitions/', '')
                                    events_data[path_modified][method]['responses']['200']['schema']['ref_def']['properties'][prop]['ref_def'] = data['definitions'][def_]
                        except:
                            pass

                        try:
                            definition = data['paths'][path][method]['responses']['400']['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['400']['schema']['ref_def'] = data['definitions'][definition]
                        except:
                            pass

                        try:
                            definition = data['paths'][path][method]['responses']['401']['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['401']['schema']['ref_def'] = data['definitions'][definition]
                        except:
                            pass

                        try:
                            definition = data['paths'][path][method]['responses']['404']['schema']['$ref'].replace('#/definitions/', '')
                            events_data[path_modified][method]['responses']['404']['schema']['ref_def'] = data['definitions'][definition]
                        except:
                            pass

        paths.sort()

        if not is_verified_user():
            flash("Your account is unverified. "
                  "Please verify by clicking on the confirmation link that has been emailed to you.")
        return self.render('/gentelella/admin/event/api/index.html',
                           event=event, data=events_data, paths=paths)
