"""
This file contains sample POST data
"""

POST_EVENT_DATA = {
    "color": "red",
    "email": "event@gmail.com",
    "end_time": "2016-05-30 12:12:43",
    "latitude": 0,
    "location_name": "TestEvent",
    "logo": "http://imgur.com/image.png",
    "longitude": 0,
    "name": "TestEvent",
    'event_url': "http://site.com",
    'background_url': "http://imgur.com/image.png",
    'description': "blah blah",
    "start_time": "2016-05-25 12:12:43",
    "closing_datetime": "2016-05-22 12:12:43",
    "organizer_name": "FOSSASIA",
    "organizer_description": "Promoting Open Source culture around the world",
    "state": "TestEvent",
    "type": "Conference",
    "topic": "Science & Technology"
}

POST_FORMAT_DATA = {
    "label_en": "TestFormat",
    "name": "TestFormat"
}

POST_LANGUAGE_DATA = {
    "label_de": "TestLanguage",
    "label_en": "TestLanguage",
    "name": "TestLanguage"
}

POST_LEVEL_DATA = {
    "label_en": "TestLevel",
    "name": "TestLevel"
}

POST_MICROLOCATION_DATA = {
    "floor": 1,
    "latitude": 1,
    "longitude": 1,
    "name": "TestMicrolocation",
    "room": "TestRoom"
}

POST_SESSION_DATA = {
    "abstract": "TestSession",
    "description": "TestSession",
    "end_time": "2016-05-30 09:47:37",
    "format_id": None,
    "language_id": None,
    "level_id": None,
    "microlocation_id": None,
    "speaker_ids": [],
    "start_time": "2016-05-30 08:47:37",
    "subtitle": "TestSession",
    "title": "TestSession",
    "track_id": None
}

POST_SPEAKER_DATA = {
    "biography": "TestSpeaker",
    "country": "TestSpeaker",
    "email": "speaker@gmail.com",
    "facebook": "http://facebook.com/user",
    "github": "http://github.com/user",
    "linkedin": "http://in.linkedin.com/user",
    "name": "TestSpeaker",
    "organisation": "TestSession",
    "photo": "http://imgur.com/skds.png",
    "position": "TestSession",
    "twitter": "http://twitter.com/user",
    "web": "http://website.com"
}

POST_SPONSOR_TYPE_DATA = {
    "name": "TestSponsor_Type",
}

POST_SPONSOR_DATA = {
    "logo": "http://imgur.com/image.png",
    "name": "TestSponsor",
    "url": "http://sponsor.com",
    "description": "Big Sponsor",
    "sponsor_type_id": 1,
}

POST_TRACK_DATA = {
    "description": "TestTrack",
    "name": "TestTrack",
    "color": "red",
    "track_image_url": "http://imgur.com/image.png",
    "location": "Some Street, Some City",
}
