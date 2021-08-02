import unittest

from app.api.schema.speakers_calls import SpeakersCallSchema
from tests.all.integration.utils import OpenEventTestCase
from tests.factories.speakers_call import SpeakersCallFactory


class TestSpeakersCallValidation(OpenEventTestCase):
    def test_date_db_populate(self):
        """
        Speakers Call Validate Date - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with self.app.test_request_context():
            schema = SpeakersCallSchema()
            SpeakersCallFactory()

            original_data = {'data': {'id': 1}}
            data = {}
            SpeakersCallSchema.validate_date(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()
