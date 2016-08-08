import unittest

from tests.api.utils_post_data import POST_EVENT_DATA
from tests.object_mother import ObjectMother
from app import current_app as app
from app.helpers.data import save_to_db
from app.models.modules import Module
from app.helpers.data_getter import DataGetter
from flask import url_for

from tests.views.view_test_case import OpenEventViewTestCase
from werkzeug.datastructures import ImmutableMultiDict


class TestEvents(OpenEventViewTestCase):
    def test_events_list(self):
        with app.test_request_context():
            url = url_for('events.index_view')
            rv = self.app.get(url, follow_redirects=True)

            self.assertTrue("Manage Events" in rv.data, msg=rv.data)

    def test_events_create(self):
        with app.test_request_context():
            url = url_for('events.create_view')
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Create Event" in rv.data, msg=rv.data)

    def test_events_create_post(self):
        with app.test_request_context():
            custom_forms = ObjectMother.get_custom_form()
            url = url_for('events.create_view')
            data = POST_EVENT_DATA.copy()
            del data['copyright']
            del data['call_for_papers']
            data['name'] = 'TestEvent 1'
            data['payment_country'] = 'United States'
            data['payment_currency'] = 'USD United States Dollars $'
            data['paypal_email'] = 'test@gmail.com'
            data['sponsors_state'] = 'on'
            data['sponsors[name]'] = ['Sponsor 1', 'Sponsor 2']
            data['sponsors[type]'] = ['Gold', 'Silver']
            data['sponsors[url]'] = ["", ""]
            data['sponsors[description]'] = ["", ""]
            data['sponsors[level]'] = ["", ""]
            data['start_date'] = '07/04/2016'
            data['start_time'] = '19:00'
            data['end_date'] = '07/04/2016'
            data['end_time'] = '22:00'
            data['has_session_speakers'] = 'no'
            data['custom_form[name]'] = ['session_form', 'speaker_form']
            data['custom_form[value]'] = [custom_forms.session_form, custom_forms.speaker_form]

            # Add Module to include Ticketing System
            save_to_db(Module(True, True, True))
            # Add Tickets
            data['tickets[name]'] = ['Free Ticket', 'Paid Ticket', 'Donation Ticket']
            data['tickets[type]'] = ['free', 'paid', 'donation']
            data['tickets[price]'] = ['', 999, '']
            data['tickets[quantity]'] = [512, 512, 512]
            data['tickets[description]'] = ['', '', '']
            data['tickets[sales_start_date]'] = ['07/04/2016', '07/04/2016', '07/04/2016']
            data['tickets[sales_start_time]'] = ['19:00', '19:00', '19:00']
            data['tickets[sales_end_date]'] = ['07/04/2016', '07/04/2016', '07/04/2016']
            data['tickets[sales_end_time]'] = ['22:00', '22:00', '22:00']
            data['tickets[min_order]'] = [2, 3, 4]
            data['tickets[max_order]'] = [5, 6, 7]

            # Add tax form to event
            data['taxAllow'] = 'taxYes'
            data['tax_country'] = 'Tax Country'
            data['tax_name'] = 'Tax Name'
            data['tax_rate'] = 1
            data['tax_id'] = 1
            data['tax_invoice'] = 'invoiceYes'
            data['registered_company'] = 'TestCompany'
            data['buisness_address'] = 'TestAddress'
            data['invoice_city'] = 'TestCity'
            data['invoice_state'] = 'TestState'
            data['tax_zip'] = 1234
            data['tax_options'] = 'tax_include'
            postdata = ImmutableMultiDict(data)
            rv = self.app.post(url, follow_redirects=True, buffered=True, content_type='multipart/form-data',
                               data=postdata)
            self.assertTrue('TestEvent 1' in rv.data, msg=rv.data)

            #Test Payment Details
            self.assertTrue(data['payment_country'] in rv.data, msg=rv.data)
            self.assertTrue(data['paypal_email'] in rv.data, msg=rv.data)

            # Test Tickets
            event = DataGetter.get_event(1)
            self.assertEqual(len(event.tickets), 3, msg=event.tickets)

            for ticket in event.tickets:
                self.assertIn(ticket.name, data['tickets[name]'], msg=data['tickets[name]'])

            #Test Tax Form
            tax = DataGetter.get_tax_options(1)
            self.assertEqual(tax.country, data['tax_country'])
            self.assertEqual(tax.tax_rate, data['tax_rate'])

            rv2 = self.app.get(url_for('events.details_view', event_id=1))
            self.assertTrue(postdata['sponsors[name]'] in rv2.data, msg=rv2.data)

    def test_events_create_post_publish(self):
        with app.test_request_context():
            url = url_for('events.create_view')
            data = POST_EVENT_DATA.copy()
            del data['copyright']
            del data['call_for_papers']
            data['payment_country'] = 'United States'
            data['payment_currency'] = 'USD United States Dollars $'
            data['start_date'] = '07/04/2016'
            data['start_time'] = '19:00'
            data['end_date'] = '07/04/2016'
            data['end_time'] = '22:00'
            data['state'] = 'Published'
            data['has_session_speakers'] = 'no'
            rv = self.app.post(url, follow_redirects=True, buffered=True, content_type='multipart/form-data',
                               data=data)
            self.assertTrue('unpublish' in rv.data, msg=rv.data)

    def test_events_create_post_publish_without_location_attempt(self):
        with app.test_request_context():
            custom_forms = ObjectMother.get_custom_form()
            url = url_for('events.create_view')
            data = POST_EVENT_DATA.copy()
            del data['copyright']
            del data['call_for_papers']
            data['payment_country'] = 'United States'
            data['payment_currency'] = 'USD United States Dollars $'
            data['start_date'] = '07/04/2016'
            data['start_time'] = '19:00'
            data['end_date'] = '07/04/2016'
            data['end_time'] = '22:00'
            data['location_name'] = ''
            data['state'] = u'Published'
            data['has_session_speakers'] = 'no'
            data['custom_form[name]'] = ['session_form', 'speaker_form']
            data['custom_form[value]'] = [custom_forms.session_form, custom_forms.speaker_form]
            rv = self.app.post(url, follow_redirects=True, buffered=True, content_type='multipart/form-data',
                               data=data)
            self.assertTrue('To publish your event please review the highlighted fields below' in rv.data, msg=rv.data)

    def test_events_edit(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            custom_forms = ObjectMother.get_custom_form(event.id)
            save_to_db(custom_forms, "Custom forms saved")
            url = url_for('events.edit_view', event_id=event.id)
            data = POST_EVENT_DATA.copy()
            del data['copyright']
            del data['call_for_papers']
            data['payment_country'] = 'United States'
            data['payment_currency'] = 'USD United States Dollars $'
            data['sponsors_state'] = 'on'
            data['sponsors[name]'] = ['Sponsor 1', 'Sponsor 2']
            data['sponsors[type]'] = ['Gold', 'Silver']
            data['sponsors[url]'] = ["", ""]
            data['sponsors[description]'] = ["", ""]
            data['sponsors[level]'] = ["", ""]
            data['name'] = 'EditTestName'
            data['start_date'] = '07/04/2016'
            data['start_time'] = '19:00'
            data['has_session_speakers'] = 'yes'
            data['end_date'] = '07/04/2016'
            data['end_time'] = '22:00'
            data['has_session_speakers'] = 'no'
            data['custom_form[name]'] = ['session_form', 'speaker_form']
            data['custom_form[value]'] = [custom_forms.session_form, custom_forms.speaker_form]
            data = ImmutableMultiDict(data)
            rv = self.app.post(url, follow_redirects=True, buffered=True, content_type='multipart/form-data',
                               data=data)
            self.assertTrue('EditTestName' in rv.data, msg=rv.data)
            self.assertTrue(data['sponsors[name]'] in rv.data, msg=rv.data)

    def test_event_view(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('events.details_view', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("event1" in rv.data, msg=rv.data)
            microlocation = ObjectMother.get_microlocation(event_id=event.id)
            track = ObjectMother.get_track(event_id=event.id)
            cfs = ObjectMother.get_cfs(event_id=event.id)
            save_to_db(track, "Track saved")
            save_to_db(microlocation, "Microlocation saved")
            save_to_db(cfs, "Call for speakers saved")
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("event1" in rv.data, msg=rv.data)

    def test_event_publish(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('events.publish_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            event = DataGetter.get_event(event.id)
            self.assertEqual("Published", event.state, msg=event.state)

    def test_event_unpublish(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            event.state = "Published"
            save_to_db(event, "Event saved")
            url = url_for('events.unpublish_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            event = DataGetter.get_event(event.id)
            self.assertEqual("Draft", event.state, msg=event.state)

    def test_event_delete(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('events.trash_view', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Your event has been deleted" in rv.data, msg=rv.data)

    def test_event_copy(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('events.copy_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Copy of event1" in rv.data, msg=rv.data)



if __name__ == '__main__':
    unittest.main()
