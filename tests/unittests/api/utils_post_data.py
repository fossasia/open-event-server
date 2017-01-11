"""
This file contains sample POST data
"""

POST_EVENT_DATA = {
    "email": "event@gmail.com",
    "end_time": "2016-05-30T12:12:43",
    "timezone": "UTC",
    "latitude": 0,
    "location_name": "Berlin",
    "searchable_location_name": "Berlin",
    "logo": "",
    "longitude": 0,
    "name": "TestEvent",
    'event_url': "http://site.com",
    'background_image': "",
    'description': "blah blah",
    "start_time": "2016-05-25T12:12:43",
    "organizer_name": "FOSSASIA",
    "organizer_description": "Promoting Open Source culture around the world",
    "state": "Draft",
    "type": "Conference",
    "topic": "Science & Technology",
    "sub_topic": "Other",
    "privacy": "public",
    "ticket_url": "http://site.com/tickets",
    "code_of_conduct": "Thou shalt be kind",
    "schedule_published_on": None,
    "copyright": {
        "holder": "FOSSASIA",
        "holder_url": "http://fossasia.org",
        "licence": "Test licence",
        "licence_url": "http://example.com",
        "year": 2016,
        "logo": ""
    },
    "call_for_papers": {
        "announcement": "<p>Wanna speak at our prestigious event. Send us a proposal</p>",
        "end_date": "2016-06-29T20:30:00",
        "privacy": "public",
        "start_date": "2016-06-29T19:30:00",
        "timezone": "UTC"
    },
    "identifier": "23c0644e",
    "has_session_speakers": True
}

POST_SOCIAL_LINK_DATA = {
    "name": "TestSocialLink",
    "link": "http://example.com"
}

POST_MICROLOCATION_DATA = {
    "floor": 1,
    "latitude": 1,
    "longitude": 1,
    "name": "TestMicrolocation",
    "room": "TestRoom"
}

POST_SESSION_DATA = {
    "short_abstract": "TestSession",
    "long_abstract": "TestSession",
    "end_time": "2016-05-30T09:47:37",
    "microlocation_id": None,
    "speaker_ids": [],
    "start_time": "2016-05-30T08:47:37",
    "subtitle": "TestSession",
    "comments": "Comments",
    "title": "TestSession",
    "track_id": None,
    "language": "German",
    "slides": "http://example.com/slides",
    "video": "http://example.com/video",
    "audio": "http://example.com/audio",
    "signup_url": "http://example.com/signup",
    "session_type_id": None,
    "level": "TestSessionLevel"
}

POST_SESSION_TYPE_DATA = {
    'name': 'TestSessionType',
    'length': '5.12'
}

POST_SPEAKER_DATA = {
    "short_biography": "TestSpeaker",
    "long_biography": "TestSpeaker",
    "country": "TestSpeaker",
    "email": "speaker@gmail.com",
    "mobile": "speaker@gmail.com",
    "facebook": "http://facebook.com/user",
    "github": "http://github.com/user",
    "linkedin": "http://in.linkedin.com/user",
    "featured": True,
    "name": "TestSpeaker",
    "organisation": "TestSession",
    "photo": "http://imgur.com/skds.png",
    "position": "TestSession",
    "twitter": "http://twitter.com/user",
    "website": "http://website.com",
    "city": "TestCity",
    "heard_from": "TestSource",
    "speaking_experience": "TestExperience",
    "sponsorship_required": "Yes"
}

POST_SPONSOR_DATA = {
    "logo": "http://imgur.com/image.png",
    "name": "TestSponsor",
    "url": "http://sponsor.com",
    "description": "Big Sponsor",
    "level": "TestSponsor",
    "sponsor_type": "Gold",
}

POST_TRACK_DATA = {
    "description": "TestTrack",
    "name": "TestTrack",
    "color": "red",
    "track_image_url": "http://imgur.com/image.png",
    "location": "Some Street, Some City",
}

POST_USER_DATA = {
    "email": "test@gmail.com",
    "password": "test"
}

PUT_USER_DATA = {
    "email": "email@domain.com",
    "user_detail": {
        "avatar": "http://website.com/image.ext",
        "contact": "string",
        "details": "TestUser",
        "facebook": "string",
        "firstname": "TestFirstName",
        "lastname": "TestLastName",
        "twitter": "string"
    }
}
