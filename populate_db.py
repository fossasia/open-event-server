from app.api.helpers.db import get_or_create

# Admin message settings
from app.api.helpers.system_mails import MailType
from app.instance import current_app
from app.models import db

# Custom Placeholder
from app.models.custom_placeholder import CustomPlaceholder
from app.models.custom_system_role import CustomSysRole

# EventLocation
from app.models.event_location import EventLocation

# EventSubTopic
from app.models.event_sub_topic import EventSubTopic

# EventTopic
from app.models.event_topic import EventTopic

# EventType
from app.models.event_type import EventType
from app.models.image_size import ImageSizes
from app.models.message_setting import MessageSettings
from app.models.microlocation import Microlocation
from app.models.notification import NotificationType
from app.models.notification_setting import NotificationSettings

# Admin Panel Permissions
from app.models.panel_permission import PanelPermission
from app.models.permission import Permission

# Event Role-Service Permissions
from app.models.role import Role
from app.models.service import Service
from app.models.session import Session
from app.models.setting import Setting
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor
from app.models.track import Track
from app.models.user import MODERATOR, REGISTRAR, TRACK_ORGANIZER

# User Permissions
from app.models.user_permission import UserPermission
from app.models.video_channel import VideoChannel

SALES = 'sales'
ADMIN = 'admin'
EVENTS = 'events'
SESSIONS = 'sessions'
USERS = 'users'
PERMISSIONS = 'permissions'
MESSAGES = 'messages'
REPORTS = 'reports'
SETTINGS = 'settings'
CONTENT = 'content'


def create_roles():
    get_or_create(Role, name=Role.ORGANIZER, defaults=dict(title_name='Organizer'))
    get_or_create(Role, name=Role.COORGANIZER, defaults=dict(title_name='Co-Organizer'))
    get_or_create(Role, name=Role.OWNER, defaults=dict(title_name='Owner'))

    # Deprecated
    get_or_create(Role, name=TRACK_ORGANIZER, defaults=dict(title_name='Track Organizer'))
    get_or_create(Role, name=MODERATOR, defaults=dict(title_name='Moderator'))
    get_or_create(Role, name=REGISTRAR, defaults=dict(title_name='Registrar'))


def create_services():
    track = Track.get_service_name()
    session = Session.get_service_name()
    speaker = Speaker.get_service_name()
    sponsor = Sponsor.get_service_name()
    microlocation = Microlocation.get_service_name()

    get_or_create(Service, name=track)
    get_or_create(Service, name=session)
    get_or_create(Service, name=speaker)
    get_or_create(Service, name=sponsor)
    get_or_create(Service, name=microlocation)


def create_settings():
    get_or_create(Setting, app_name='Open Event')


def create_event_image_sizes():
    get_or_create(
        ImageSizes,
        type='event-image',
        full_width=1300,
        full_height=500,
        full_aspect=True,
        full_quality=80,
        icon_width=75,
        icon_height=30,
        icon_aspect=True,
        icon_quality=80,
        thumbnail_width=500,
        thumbnail_height=200,
        thumbnail_aspect=True,
        thumbnail_quality=80,
        logo_width=500,
        logo_height=200,
    )


def create_speaker_image_sizes():
    get_or_create(
        ImageSizes,
        type='speaker-image',
        icon_size_width_height=35,
        icon_size_quality=80,
        small_size_width_height=50,
        small_size_quality=80,
        thumbnail_size_width_height=500,
        thumbnail_quality=80,
    )


def create_event_topics():
    event_topic = [
        'Health & Wellness',
        'Home & Lifestyle',
        'Charity & Causes',
        'Other',
        'Religion & Spirituality',
        'Community & Culture',
        'Government & Politics',
        'Government & Politics',
        'Auto, Boat & Air',
        'Travel & Outdoor',
        'Hobbies & Special Interest',
        'Sports & Fitness',
        'Business & Professional',
        'Music',
        'Seasonal & Holiday',
        'Film, Media & Entertainment',
        'Family & Education',
        'Science & Technology',
        'Performing & Visual Arts',
        'Food & Drink',
        'Family & Education',
    ]
    for topic in event_topic:
        get_or_create(EventTopic, name=topic)


def create_event_sub_topics():
    event_sub_topic = {
        "Film, Media & Entertainment": ["Comedy", "Gaming", "Anime"],
        "Community & Culture": ["City/Town", "Other", "LGBT"],
        "Home & Lifestyle": ["Dating", "Home & Garden"],
        "Sports & Fitness": ["Volleyball", "Other"],
        "Health & Wellness": ["Yoga", "Medical"],
        "Food & Drink": ["Other", "Food", "Beer"],
        "Other": ["Avatar", "Logo"],
        "Science & Technology": [
            "Robotics",
            "Other",
            "High Tech",
            "Science",
            "Social Media",
            "Medicine",
            "Mobile",
            "Biotech",
        ],
        "Music": [
            "Cultural",
            "Pop",
            "Top 40",
            "EDM / Electronic",
            "R&B",
            "Other",
            "Classical",
        ],
        "Performing & Visual Arts": ["Craft", "Comedy", "Fine Art", "Orchestra"],
        "Family & Education": ["Education", "Baby", "Reunion"],
        "Business & Professional": [
            "Career",
            "Startups & Small Business",
            "Educators",
            "Design",
            "Finance",
        ],
        "Charity & Causes": ["Education", "Other", "Environment"],
        "Hobbies & Special Interest": ["Other", "Anime/Comics"],
        "Seasonal & Holiday": ["Easter", "Other"],
        "Auto, Boat & Air": ["Auto", "Air"],
        "Religion & Spirituality": ["Mysticism and Occult"],
        "Government & Politics": ["Non-partisan"],
    }
    eventopics = db.session.query(EventTopic).all()
    for keysub_topic in event_sub_topic:
        for subtopic in event_sub_topic[keysub_topic]:
            get_or_create(
                EventSubTopic,
                name=subtopic,
                event_topic_id=next(x for x in eventopics if x.name == keysub_topic).id,
            )


def create_event_types():
    event_type = [
        'Camp, Treat & Retreat',
        'Dinner or Gala',
        'Other',
        'Concert or Performance',
        'Conference',
        'Seminar or Talk',
        'Convention',
        'Festival or Fair',
        'Tour',
        'Screening',
        'Game or Competition',
        'Party or Social Gathering',
        'Race or Endurance Event',
        'Meeting or Networking Event',
        'Attraction',
        'Class, Training, or Workshop',
        'Appearance or Signing',
        'Tournament',
        'Rally',
    ]
    for type_ in event_type:
        get_or_create(EventType, name=type_)


def create_event_locations():
    event_location = ['India', 'Singapore', 'Berlin', 'New York', 'Hong Kong']
    for loc_ in event_location:
        get_or_create(EventLocation, name=loc_)


def create_permissions():
    ownr = Role.query.filter_by(name=Role.OWNER).first()
    orgr = Role.query.filter_by(name=Role.ORGANIZER).first()
    coorgr = Role.query.filter_by(name=Role.COORGANIZER).first()
    track_orgr = Role.query.filter_by(name=TRACK_ORGANIZER).first()
    mod = Role.query.filter_by(name=MODERATOR).first()
    regist = Role.query.filter_by(name=REGISTRAR).first()
    track = Service.query.filter_by(name=Track.get_service_name()).first()
    session = Service.query.filter_by(name=Session.get_service_name()).first()
    speaker = Service.query.filter_by(name=Speaker.get_service_name()).first()
    sponsor = Service.query.filter_by(name=Sponsor.get_service_name()).first()
    microlocation = Service.query.filter_by(name=Microlocation.get_service_name()).first()

    # For ORGANIZER and OWNER
    # All four permissions set to True
    services = [track, session, speaker, sponsor, microlocation]
    for service in services:
        perm, _ = get_or_create(Permission, role=ownr, service=service)
        db.session.add(perm)

    for service in services:
        perm, _ = get_or_create(Permission, role=orgr, service=service)
        db.session.add(perm)

    # For COORGANIZER
    for service in services:
        perm, _ = get_or_create(Permission, role=coorgr, service=service)
        perm.can_create, perm.can_delete = False, False
        db.session.add(perm)

    # For TRACK_ORGANIZER
    for service in services:
        perm, _ = get_or_create(Permission, role=track_orgr, service=service)
        if not service == track:
            perm.can_create, perm.can_update, perm.can_delete = False, False, False
        db.session.add(perm)

    # For MODERATOR
    for service in services:
        perm, _ = get_or_create(Permission, role=mod, service=service)
        perm.can_create, perm.can_update, perm.can_delete = False, False, False
        db.session.add(perm)

    # For REGISTRAR
    services = [track, session, speaker, sponsor, microlocation]
    for service in services:
        perm, _ = get_or_create(Permission, role=regist, service=service)
        perm.can_create, perm.can_update, perm.can_delete = False, False, False
        db.session.add(perm)


def create_custom_sys_roles():
    role, _ = get_or_create(CustomSysRole, name='Sales Admin')
    db.session.add(role)
    role, _ = get_or_create(CustomSysRole, name='Marketer')
    db.session.add(role)


def create_panels():
    panels = [
        SALES,
        ADMIN,
        EVENTS,
        SESSIONS,
        USERS,
        PERMISSIONS,
        MESSAGES,
        REPORTS,
        SETTINGS,
        CONTENT,
    ]
    for panel in panels:
        perm, _ = get_or_create(PanelPermission, panel_name=panel)
        db.session.add(perm)


def create_panel_permissions():
    sales_panel, _ = get_or_create(PanelPermission, panel_name=SALES)
    sales_admin, _ = get_or_create(CustomSysRole, name='Sales Admin')
    marketer, _ = get_or_create(CustomSysRole, name='Marketer')
    sales_panel.custom_system_roles.append(sales_admin)
    sales_panel.custom_system_roles.append(marketer)


def create_user_permissions():
    # Publish Event
    user_perm, _ = get_or_create(
        UserPermission,
        name='publish_event',
        description='Publish event (make event live)',
    )
    user_perm.verified_user = True
    db.session.add(user_perm)

    # Create Event
    user_perm, _ = get_or_create(
        UserPermission, name='create_event', description='Create event'
    )
    user_perm.verified_user, user_perm.unverified_user = True, False
    db.session.add(user_perm)


def create_admin_message_settings():
    for mail in MailType.entries():
        get_or_create(MessageSettings, action=mail, defaults=dict(enabled=True))
    for notification in NotificationType.entries():
        get_or_create(
            NotificationSettings, type=notification, defaults=dict(enabled=True)
        )


def create_custom_placeholders():
    custom_placeholder, _ = get_or_create(
        CustomPlaceholder,
        name='Hills',
        original_image_url='https://www.w3schools.com/html/pic_mountain.jpg',
        event_sub_topic_id=1,
    )
    db.session.add(custom_placeholder)


def populate():
    """
    Create defined Roles, Services and Permissions.
    """
    print('Creating roles...')
    create_roles()
    print('Creating services...')
    create_services()
    print('Creating permissions...')
    create_permissions()
    print('Creating custom system roles...')
    create_custom_sys_roles()
    print('Creating panels...')
    create_panels()
    print('Creating admin panel permissions...')
    create_panel_permissions()
    print('Creating user permissions...')
    create_user_permissions()
    print('Creating settings...')
    create_settings()
    print('Creating event image size...')
    create_event_image_sizes()
    print('Creating speaker image size...')
    create_speaker_image_sizes()
    print('Creating Event Topics...')
    create_event_topics()
    print('Creating Event SubTopics...')
    create_event_sub_topics()
    print('Creating Event Types...')
    create_event_types()
    print('Creating Event Locations...')
    create_event_locations()
    print('Creating admin message settings...')
    create_admin_message_settings()
    print('Creating custom placeholders...')
    create_custom_placeholders()
    get_or_create(
        VideoChannel,
        provider='jitsi',
        name='Jitsi Meet',
        defaults={'url': 'https://meet.jit.si', 'api_url': 'https://api.jitsi.net'},
    )
    get_or_create(
        VideoChannel,
        provider='youtube',
        name='YouTube',
        defaults={
            'url': 'https://youtube.com',
            'api_url': 'https://www.googleapis.com/youtube/v3',
        },
    )
    get_or_create(
        VideoChannel,
        provider='vimeo',
        name='Vimeo',
        defaults={'url': 'https://vimeo.com', 'api_url': 'https://api.vimeo.com'},
    )
    get_or_create(
        VideoChannel,
        provider='3cx',
        name='3CX',
        defaults={'url': 'https://www.3cx.com/'},
    )
    get_or_create(
        VideoChannel,
        provider='chatmosphere',
        name='Chatmosphere',
        defaults={'url': 'https://app.chatmosphere.cc/'},
    )
    get_or_create(
        VideoChannel,
        provider='libre',
        name='Libre Work',
        defaults={'url': 'https://2d.freiland-potsdam.de/'},
    )

    db.session.commit()


if __name__ == '__main__':
    with current_app.app_context():
        populate()
