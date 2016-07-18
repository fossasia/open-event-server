import unittest
from tests.utils import OpenEventTestCase
from app.models.social_link import SocialLink
from tests.setup_database import Setup
from app import current_app as app
from app.helpers.data import save_to_db
from tests.object_mother import ObjectMother


class TestSocialLink(OpenEventTestCase):
    def test_add_social_link_to_db(self):
        """Checks the one to many relationship between event and social_links """
        self.app = Setup.create_app()
        with app.test_request_context():
            event = ObjectMother.get_event()
            social_link1 = SocialLink(name='Link1', link='some_random_link_1', event_id='1')
            social_link2 = SocialLink(name='Link2', link='some_random_link_2', event_id='1')
            save_to_db(event, "Event Saved")
            save_to_db(social_link1, "SocialLink1 Saved")
            save_to_db(social_link2, "SocialLink2 Saved")
            self.assertEqual(social_link1.event_id, 1)
            self.assertEqual(social_link2.event_id, 1)


if __name__ == '__main__':
    unittest.main()
