import base64
from datetime import datetime, timedelta

import qrcode
from StringIO import StringIO

from app.helpers.payment import forex
from app.helpers.data_getter import DataGetter


def init_helpers(app):
    @app.context_processor
    def flask_helpers():

        def get_locations_of_events():
            return DataGetter.get_locations_of_events()

        def get_fee(currency):
            from app.helpers.payment import get_fee
            return get_fee(currency)

        def string_empty(string):
            from app.helpers.helpers import string_empty
            return string_empty(string)

        def current_date(format='%a, %B %d %I:%M %p', **kwargs):
            return (datetime.now() + timedelta(**kwargs)).strftime(format)

        def generate_qr(text):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=0,
            )
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image()

            buffer = StringIO()
            img.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue())
            return img_str

        return dict(
            string_empty=string_empty,
            current_date=current_date,
            forex=forex,
            locations=get_locations_of_events,
            get_fee=get_fee,
            generate_qr=generate_qr
        )

    @app.context_processor
    def versioning_manager():
        def count_versions(model_object):
            from sqlalchemy_continuum.utils import count_versions
            return count_versions(model_object)

        def changeset(model_object):
            from sqlalchemy_continuum import changeset
            return changeset(model_object)

        def transaction_class(version_object):
            from sqlalchemy_continuum import transaction_class
            transaction = transaction_class(version_object)
            return transaction.query.get(version_object.transaction_id)

        def version_class(model_object):
            from sqlalchemy_continuum import version_class
            return version_class(model_object)

        def get_user_name(transaction_object):
            if transaction_object and transaction_object.user_id:
                user = DataGetter.get_user(transaction_object.user_id)
                return user.email
            return 'unconfigured@example.com'

        def side_by_side_diff(changeset_entry):
            from app.helpers.versioning import side_by_side_diff
            for side_by_side_diff_entry in side_by_side_diff(changeset_entry[0],
                                                             changeset_entry[1]):
                yield side_by_side_diff_entry

        return dict(count_versions=count_versions,
                    changeset=changeset,
                    transaction_class=transaction_class,
                    version_class=version_class,
                    side_by_side_diff=side_by_side_diff,
                    get_user_name=get_user_name)
