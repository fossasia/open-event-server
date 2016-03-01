from open_event import current_app
from open_event.helpers.data import get_or_create, save_to_db

from open_event.models.session import Session, Level, Format, Language
from open_event.models.speaker import Speaker
from open_event.models.track import Track

from datetime import datetime

class Saver(object):

    def __init__(self, row, event_id, date, end_time, track_name):
        self.row = row
        self.event_id = event_id
        self.date = date
        self.end_time = end_time
        self.track_name = track_name

    def _save(self):
        speakers = []

        try:
            session_date, session_time, name, fam_name, company, email, web, mobile_phone, github, bitbucket, twitter, linkedin, country, city, photo, type, topic, __, abstract, bio = self._get_values()

            if name == "" and fam_name == "" and company == "" and email == "":
                return

            with current_app.app_context():

                sp = get_or_create(Speaker,
                                    name=name + ' ' + fam_name,
                                    email=email,
                                    photo=photo,
                                    web=web,
                                    event_id=self.event_id,
                                    twitter=twitter,
                                    github=github,
                                    linkedin=linkedin,
                                    organisation=company,
                                    country=country)

                speakers.append(sp)

                new_session = get_or_create(Session,
                                            title=topic,
                                            event_id=self.event_id,
                                            is_accepted=True,
                                            description = bio,
                                            start_time = datetime.strptime(self.date, "%Y %A %B %d %H:%M"),
                                            end_time = datetime.strptime(self.end_time, "%Y %A %B %d %H:%M"),
                                            abstract = abstract)


                new_session.speakers = speakers
                new_session.track = get_or_create(Track, name=self.track_name, description="", event_id=self.event_id, track_image_url="")
                save_to_db(new_session, "Session Updated")
        except Exception as e:
            print e

    def _get_values(self):
        row = self.row
        session_date = row[0].value
        session_time = row[1].value
        name = row[3].value
        fam_name = row[4].value
        company = row[5].value
        email = row[6].value
        web = row[7].value
        mobile_phone = row[8].value
        phone = row[9].value
        github = row[10].value
        bitbucket = row[11].value
        twitter = row[12].value
        linkedin = row[13].value
        skype = row[14].value
        country = row[15].value
        city = row[16].value
        address = row[17].value
        photo = row[18].value
        type = row[19].value
        topic = row[20].value
        track = row[21].value
        abstract = row[22].value
        bio = row[23].value

        return session_date, session_time, name, fam_name, company, email, web, mobile_phone, github, bitbucket, twitter, linkedin, country, city, photo, type, topic, track, abstract, bio



