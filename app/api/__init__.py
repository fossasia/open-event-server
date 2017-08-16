from app.api.bootstrap import api
from app.api.stripe_authorization import StripeAuthorizationList, StripeAuthorizationDetail, \
    StripeAuthorizationRelationship, StripeAuthorizationListPost
from app.api.ticket_fees import TicketFeeList, TicketFeeDetail
from app.api.users import UserList, UserDetail, UserRelationship
from app.api.notifications import NotificationList, NotificationListAdmin, NotificationDetail, NotificationRelationship
from app.api.email_notifications import EmailNotificationList, EmailNotificationListAdmin, EmailNotificationDetail,\
    EmailNotificationRelationshipOptional, EmailNotificationRelationshipRequired
from app.api.tickets import TicketList, TicketListPost, TicketDetail, TicketRelationshipRequired,\
    TicketRelationshipOptional
from app.api.events import EventList, EventDetail, EventRelationship
from app.api.event_types import EventTypeList, EventTypeDetail, EventTypeRelationship
from app.api.event_topics import EventTopicList, EventTopicDetail, EventTopicRelationship
from app.api.event_sub_topics import EventSubTopicList, EventSubTopicListPost, EventSubTopicDetail,\
    EventSubTopicRelationshipRequired, EventSubTopicRelationshipOptional
from app.api.microlocations import MicrolocationList, MicrolocationListPost, MicrolocationDetail, \
    MicrolocationRelationshipRequired, MicrolocationRelationshipOptional
from app.api.sessions import SessionList, SessionListPost, SessionDetail, SessionRelationshipRequired, \
    SessionRelationshipOptional
from app.api.speakers import SpeakerList, SpeakerListPost, SpeakerDetail, SpeakerRelationshipRequired,\
    SpeakerRelationshipOptional
from app.api.social_links import SocialLinkList, SocialLinkListPost, SocialLinkDetail, SocialLinkRelationship
from app.api.sponsors import SponsorList, SponsorListPost, SponsorDetail, SponsorRelationship
from app.api.tracks import TrackList, TrackListPost, TrackDetail, TrackRelationshipOptional, TrackRelationshipRequired
from app.api.speakers_calls import SpeakersCallList, SpeakersCallDetail, SpeakersCallRelationship
from app.api.event_invoices import EventInvoiceList, EventInvoiceDetail, \
    EventInvoiceRelationshipRequired, EventInvoiceRelationshipOptional
from app.api.role_invites import RoleInviteListPost, RoleInviteList, RoleInviteDetail, RoleInviteRelationship
from app.api.image_sizes import ImageSizeList, ImageSizeDetail
from app.api.roles import RoleList, RoleDetail
from app.api.session_types import SessionTypeList, SessionTypeListPost, SessionTypeDetail,\
    SessionTypeRelationshipRequired, SessionTypeRelationshipOptional
from app.api.event_copyright import EventCopyrightListPost, EventCopyrightDetail, EventCopyrightRelationshipRequired
from app.api.pages import PageList, PageDetail
from app.api.user_permission import UserPermissionList, UserPermissionDetail
from app.api.tax import TaxList, TaxListPost, TaxDetail, TaxRelationship
from app.api.settings import SettingDetail
from app.api.discount_codes import DiscountCodeList, DiscountCodeDetail, DiscountCodeRelationshipOptional, \
    DiscountCodeRelationshipRequired, DiscountCodeListPost
from app.api.ticket_tags import TicketTagList, TicketTagListPost, TicketTagDetail, TicketTagRelationshipOptional, \
    TicketTagRelationshipRequired
from app.api.attendees import AttendeeList, AttendeeDetail, AttendeeRelationshipOptional, \
    AttendeeRelationshipRequired, AttendeeListPost
from app.api.access_codes import AccessCodeList, AccessCodeListPost, AccessCodeDetail, AccessCodeRelationshipRequired, \
    AccessCodeRelationshipOptional
from app.api.custom_forms import CustomFormList, CustomFormListPost, CustomFormDetail, CustomFormRelationshipRequired
from app.api.modules import ModuleDetail
from app.api.custom_placeholders import CustomPlaceholderList, CustomPlaceholderDetail, CustomPlaceholderRelationship
from app.api.activities import ActivityList, ActivityDetail
from app.api.orders import OrdersList, OrderDetail, OrderRelationship, ChargeList, OrdersListPost
from app.api.event_statistics import EventStatisticsGeneralDetail
from app.api.mails import MailList, MailDetail
from app.api.admin_statistics_api.sessions import AdminStatisticsSessionDetail
from app.api.admin_statistics_api.events import AdminStatisticsEventDetail
from app.api.admin_statistics_api.users import AdminStatisticsUserDetail
from app.api.admin_statistics_api.mails import AdminStatisticsMailDetail
from app.api.order_statistics.events import OrderStatisticsEventDetail
from app.api.order_statistics.tickets import OrderStatisticsTicketDetail


# users
api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>', '/notifications/<int:notification_id>/user',
          '/event-invoices/<int:event_invoice_id>/user', '/speakers/<int:speaker_id>/user',
          '/access-codes/<int:access_code_id>/marketer', '/email-notifications/<int:email_notification_id>/user',
          '/discount-codes/<int:discount_code_id>/marketer', '/sessions/<int:session_id>/creator',
          '/attendees/<int:attendee_id>/user')
api.route(UserRelationship, 'user_notification', '/users/<int:id>/relationships/notifications')
api.route(UserRelationship, 'user_event_invoices', '/users/<int:id>/relationships/event-invoices')
api.route(UserRelationship, 'user_speaker', '/users/<int:id>/relationships/speakers')
api.route(UserRelationship, 'user_session', '/users/<int:id>/relationships/sessions')
api.route(UserRelationship, 'user_access_codes', '/users/<int:id>/relationships/access-codes')
api.route(UserRelationship, 'user_discount_codes', '/users/<int:id>/relationships/discount-codes')
api.route(UserRelationship, 'user_email_notifications', '/users/<int:id>/relationships/email-notifications')
api.route(UserRelationship, 'user_organizer_event', '/users/<int:id>/relationships/organizer-events')
api.route(UserRelationship, 'user_coorganizer_event', '/users/<int:id>/relationships/coorganizer-events')
api.route(UserRelationship, 'user_track_organizer_event', '/users/<int:id>/relationships/track-organizer-events')
api.route(UserRelationship, 'user_registrar_event', '/users/<int:id>/relationships/registrar-events')
api.route(UserRelationship, 'user_moderator_event', '/users/<int:id>/relationships/moderator-events')
api.route(UserRelationship, 'user_attendees', '/users/<int:id>/relationships/attendees')
api.route(UserRelationship, 'user_events', '/users/<int:id>/relationships/events')

# notifications
api.route(NotificationListAdmin, 'notification_list_admin', '/notifications')
api.route(NotificationList, 'notification_list', '/users/<int:user_id>/notifications')
api.route(NotificationDetail, 'notification_detail', '/notifications/<int:id>')
api.route(NotificationRelationship, 'notification_user',
          '/notifications/<int:id>/relationships/user')

# email_notifications
api.route(EmailNotificationListAdmin, 'email_notification_list_admin', '/email-notifications')
api.route(EmailNotificationList, 'email_notification_list', '/users/<int:id>/email-notifications')
api.route(EmailNotificationDetail, 'email_notification_detail', '/email-notifications/<int:id>')
api.route(EmailNotificationRelationshipRequired, 'email_notification_user',
          '/email-notifications/<int:id>/relationships/user')
api.route(EmailNotificationRelationshipOptional, 'email_notification_event',
          '/email-notifications/<int:id>/relationships/event')

# image_sizes
api.route(ImageSizeList, 'image_size_list', '/image-sizes')
api.route(ImageSizeDetail, 'image_size_detail', '/image-sizes/<int:id>')

# settings
api.route(SettingDetail, 'setting_detail', '/settings/<id>', '/settings')

# modules
api.route(ModuleDetail, 'module_detail', '/modules/<id>', '/modules')

# pages
api.route(PageList, 'page_list', '/pages')
api.route(PageDetail, 'page_detail', '/pages/<int:id>')


# Mails API
api.route(MailList, 'mail_list', '/mails')
api.route(MailDetail, 'mail_detail', '/mails/<int:id>')

# user-permissions
api.route(UserPermissionList, 'user_permission_list', '/user-permissions')
api.route(UserPermissionDetail, 'user_permission_detail', '/user-permissions/<int:id>')

# roles
api.route(RoleList, 'role_list', '/roles')
api.route(RoleDetail, 'role_detail', '/roles/<int:id>', '/role-invites/<int:role_invite_id>/role')

# role_invites
api.route(RoleInviteListPost, 'role_invite_list_post', '/role-invites')
api.route(RoleInviteList, 'role_invite_list', '/events/<int:event_id>/role-invites',
          '/events/<event_identifier>/role-invites')
api.route(RoleInviteDetail, 'role_invite_detail', '/role-invites/<int:id>')
api.route(RoleInviteRelationship, 'role_invite_event', '/role-invites/<int:id>/relationships/event')
api.route(RoleInviteRelationship, 'role_invite_role', '/role-invites/<int:id>/relationships/role')

# tickets
api.route(TicketListPost, 'ticket_list_post', '/tickets')
api.route(TicketList, 'ticket_list', '/events/<int:event_id>/tickets',
          '/events/<event_identifier>/tickets', '/ticket-tags/<int:ticket_tag_id>/tickets',
          '/access-codes/<int:access_code_id>/tickets', '/orders/<order_identifier>/tickets')
api.route(TicketDetail, 'ticket_detail', '/tickets/<int:id>', '/attendees/<int:attendee_id>/ticket')
api.route(TicketRelationshipRequired, 'ticket_event', '/tickets/<int:id>/relationships/event')
api.route(TicketRelationshipOptional, 'ticket_ticket_tag', '/tickets/<int:id>/relationships/ticket-tags')
api.route(TicketRelationshipOptional, 'ticket_access_code', '/tickets/<int:id>/relationships/access-codes')
api.route(TicketRelationshipOptional, 'ticket_attendees', '/tickets/<int:id>/relationships/attendees')

# ticket_tags
api.route(TicketTagListPost, 'ticket_tag_list_post', '/ticket-tags')
api.route(TicketTagList, 'ticket_tag_list', '/tickets/<int:ticket_id>/ticket-tags',
          '/events/<int:event_id>/ticket-tags', '/events/<event_identifier>/ticket-tags')
api.route(TicketTagDetail, 'ticket_tag_detail', '/ticket-tags/<int:id>')
api.route(TicketTagRelationshipOptional, 'ticket_tag_ticket', '/ticket-tags/<int:id>/relationships/tickets')
api.route(TicketTagRelationshipRequired, 'ticket_tag_event', '/ticket-tags/<int:id>/relationships/event')

# events
api.route(EventList, 'event_list', '/events', '/event-types/<int:event_type_id>/events',
          '/event-topics/<int:event_topic_id>/events',
          '/event-sub-topics/<int:event_sub_topic_id>/events', '/discount-codes/<int:discount_code_id>/events',
          '/users/<int:user_id>/events')
api.route(EventDetail, 'event_detail', '/events/<int:id>', '/events/<identifier>',
          '/tickets/<int:ticket_id>/event', '/microlocations/<int:microlocation_id>/event',
          '/social-links/<int:social_link_id>/event',
          '/sponsors/<int:sponsor_id>/event', '/tracks/<int:track_id>/event',
          '/speakers-calls/<int:speakers_call_id>/event', '/session-types/<int:session_type_id>/event',
          '/event-copyrights/<int:copyright_id>/event', '/tax/<int:tax_id>/event',
          '/event-invoices/<int:event_invoice_id>/event', '/discount-codes/<int:discount_code_id>/event',
          '/sessions/<int:session_id>/event', '/ticket-tags/<int:ticket_tag_id>/event',
          '/role-invites/<int:role_invite_id>/event', '/speakers/<int:speaker_id>/event',
          '/access-codes/<int:access_code_id>/event', '/email-notifications/<int:email_notification_id>/event',
          '/attendees/<int:attendee_id>/event', '/custom-forms/<int:custom_form_id>/event',
          '/orders/<order_identifier>/event')
api.route(EventRelationship, 'event_ticket', '/events/<int:id>/relationships/tickets',
          '/events/<identifier>/relationships/tickets')
api.route(EventRelationship, 'event_ticket_tag', '/events/<int:id>/relationships/ticket-tags',
          '/events/<identifier>/relationships/ticket-tags')
api.route(EventRelationship, 'event_microlocation', '/events/<int:id>/relationships/microlocations',
          '/events/<identifier>/relationships/microlocations')
api.route(EventRelationship, 'event_social_link', '/events/<int:id>/relationships/social-links',
          '/events/<identifier>/relationships/social-links')
api.route(EventRelationship, 'event_sponsor', '/events/<int:id>/relationships/sponsors',
          '/events/<identifier>/relationships/sponsors')
api.route(EventRelationship, 'event_tracks', '/events/<int:id>/relationships/tracks',
          '/events/<identifier>/relationships/tracks')
api.route(EventRelationship, 'event_speakers_call', '/events/<int:id>/relationships/speakers-call',
          '/events/<identifier>/relationships/speakers-call')
api.route(EventRelationship, 'event_session_types', '/events/<int:id>/relationships/session-types',
          '/events/<identifier>/relationships/session-types')
api.route(EventRelationship, 'event_copyright', '/events/<int:id>/relationships/event-copyright',
          '/events/<identifier>/relationships/event-copyright')
api.route(EventRelationship, 'event_tax', '/events/<int:id>/relationships/tax',
          '/events/<identifier>/relationships/tax')
api.route(EventRelationship, 'event_event_invoice', '/events/<int:id>/relationships/event-invoices',
          '/events/<identifier>/relationships/event-invoices')
api.route(EventRelationship, 'event_discount_code', '/events/<int:id>/relationships/discount-codes',
          '/events/<identifier>/relationships/discount-codes')
api.route(EventRelationship, 'event_session', '/events/<int:id>/relationships/sessions',
          '/events/<identifier>/relationships/sessions')
api.route(EventRelationship, 'event_event_type', '/events/<int:id>/relationships/event-type',
          '/events/<identifier>/relationships/event-type')
api.route(EventRelationship, 'event_event_topic', '/events/<int:id>/relationships/event-topic',
          '/events/<identifier>/relationships/event-topic')
api.route(EventRelationship, 'event_event_sub_topic', '/events/<int:id>/relationships/event-sub-topic',
          '/events/<identifier>/relationships/event-sub-topic')
api.route(EventRelationship, 'event_role_invite', '/events/<int:id>/relationships/role-invites',
          '/events/<identifier>/relationships/role-invites')
api.route(EventRelationship, 'event_speaker', '/events/<int:id>/relationships/speakers',
          '/events/<identifier>/relationships/speakers')
api.route(EventRelationship, 'event_access_codes', '/events/<int:id>/relationships/access-codes',
          '/events/<identifier>/relationships/access-codes')
api.route(EventRelationship, 'event_attendees', '/events/<int:id>/relationships/attendees',
          '/events/<identifier>/relationships/attendees')
api.route(EventRelationship, 'event_custom_forms', '/events/<int:id>/relationships/custom-forms',
          '/events/<identifier>/relationships/custom-forms')
api.route(EventRelationship, 'event_orders', '/events/<int:id>/relationships/orders',
          '/events/<identifier>/relationships/orders')
# Events -> roles:
api.route(EventRelationship, 'event_organizers', '/events/<int:id>/relationships/organizers',
          '/events/<identifier>/relationships/organizers')
api.route(EventRelationship, 'event_coorganizers', '/events/<int:id>/relationships/coorganizers',
          '/events/<identifier>/relationships/coorganizers')
api.route(EventRelationship, 'event_track_organizers', '/events/<int:id>/relationships/track-organizers',
          '/events/<identifier>/relationships/track-organizers')
api.route(EventRelationship, 'event_moderators', '/events/<int:id>/relationships/moderators',
          '/events/<identifier>/relationships/moderators')
api.route(EventRelationship, 'event_registrars', '/events/<int:id>/relationships/registrars',
          '/events/<identifier>/relationships/registrars')



# microlocations
api.route(MicrolocationList, 'microlocation_list', '/events/<int:event_id>/microlocations',
          '/events/<event_identifier>/microlocations')
api.route(MicrolocationListPost, 'microlocation_list_post', '/microlocations')
api.route(MicrolocationDetail, 'microlocation_detail', '/microlocations/<int:id>',
          '/sessions/<int:session_id>/microlocation')
api.route(MicrolocationRelationshipOptional, 'microlocation_session',
          '/microlocations/<int:id>/relationships/sessions')
api.route(MicrolocationRelationshipRequired, 'microlocation_event',
          '/microlocations/<int:id>/relationships/event')

# sessions
api.route(SessionListPost, 'session_list_post', '/sessions')
api.route(SessionList, 'session_list', '/events/<int:event_id>/sessions',
          '/events/<event_identifier>/sessions', '/users/<int:user_id>/sessions',
          '/tracks/<int:track_id>/sessions', '/session-types/<int:session_type_id>/sessions',
          '/microlocations/<int:microlocation_id>/sessions', '/speakers/<int:speaker_id>/sessions')
api.route(SessionDetail, 'session_detail', '/sessions/<int:id>')
api.route(SessionRelationshipOptional, 'session_microlocation',
          '/sessions/<int:id>/relationships/microlocation')
api.route(SessionRelationshipOptional, 'session_track', '/sessions/<int:id>/relationships/track')
api.route(SessionRelationshipOptional, 'session_session_type',
          '/sessions/<int:id>/relationships/session-type')
api.route(SessionRelationshipRequired, 'session_event',
          '/sessions/<int:id>/relationships/event')
api.route(SessionRelationshipRequired, 'session_user',
          '/sessions/<int:id>/relationships/creator')
api.route(SessionRelationshipOptional, 'session_speaker',
          '/sessions/<int:id>/relationships/speakers')

# social_links
api.route(SocialLinkListPost, 'social_link_list_post', '/social-links')
api.route(SocialLinkList, 'social_link_list', '/events/<int:event_id>/social-links',
          '/events/<event_identifier>/social-links')
api.route(SocialLinkDetail, 'social_link_detail', '/social-links/<int:id>')
api.route(SocialLinkRelationship, 'social_link_event',
          '/social-links/<int:id>/relationships/event')

# sponsors
api.route(SponsorListPost, 'sponsor_list_post', '/sponsors')
api.route(SponsorList, 'sponsor_list', '/events/<int:event_id>/sponsors',
          '/events/<event_identifier>/sponsors')
api.route(SponsorDetail, 'sponsor_detail', '/sponsors/<int:id>')
api.route(SponsorRelationship, 'sponsor_event', '/sponsors/<int:id>/relationships/event')

# tracks
api.route(TrackListPost, 'track_list_post', '/tracks')
api.route(TrackList, 'track_list', '/events/<int:event_id>/tracks',
          '/events/<event_identifier>/tracks')
api.route(TrackDetail, 'track_detail', '/tracks/<int:id>', '/sessions/<int:session_id>/track')
api.route(TrackRelationshipOptional, 'track_sessions', '/tracks/<int:id>/relationships/sessions')
api.route(TrackRelationshipRequired, 'track_event', '/tracks/<int:id>/relationships/event')

# speakers_calls
api.route(SpeakersCallList, 'speakers_call_list', '/speakers-calls')
api.route(SpeakersCallDetail, 'speakers_call_detail', '/speakers-calls/<int:id>',
          '/events/<int:event_id>/speakers-call', '/events/<event_identifier>/speakers-call')
api.route(SpeakersCallRelationship, 'speakers_call_event',
          '/speakers-calls/<int:id>/relationships/event')

# session_types
api.route(SessionTypeListPost, 'session_type_list_post', '/session-types')
api.route(SessionTypeList, 'session_type_list', '/events/<int:event_id>/session-types',
          '/events/<event_identifier>/session-types')
api.route(SessionTypeDetail, 'session_type_detail', '/session-types/<int:id>',
          '/sessions/<int:session_id>/session-type')
api.route(SessionTypeRelationshipOptional, 'session_type_sessions',
          '/session-types/<int:id>/relationships/sessions')
api.route(SessionTypeRelationshipRequired, 'session_type_event',
          '/session-types/<int:id>/relationships/event')

# speakers
api.route(SpeakerListPost, 'speaker_list_post', '/speakers')
api.route(SpeakerList, 'speaker_list', '/events/<int:event_id>/speakers',
          '/events/<event_identifier>/speakers',
          '/sessions/<int:session_id>/speakers', '/users/<int:user_id>/speakers')
api.route(SpeakerDetail, 'speaker_detail', '/speakers/<int:id>')
api.route(SpeakerRelationshipRequired, 'speaker_event', '/speakers/<int:id>/relationships/event')
api.route(SpeakerRelationshipRequired, 'speaker_user', '/speakers/<int:id>/relationships/user')
api.route(SpeakerRelationshipOptional, 'speaker_session', '/speakers/<int:id>/relationships/sessions')

# event_copyright
api.route(EventCopyrightListPost, 'event_copyright_list_post', '/event-copyrights')
api.route(EventCopyrightDetail, 'event_copyright_detail',
          '/event-copyrights/<int:id>', '/events/<int:event_id>/event-copyright',
          '/events/<event_identifier>/event-copyright')
api.route(EventCopyrightRelationshipRequired, 'copyright_event',
          '/event-copyrights/<int:id>/relationships/event')

# custom_placeholder
api.route(CustomPlaceholderList, 'custom_placeholder_list',
          '/custom-placeholders')
api.route(CustomPlaceholderDetail, 'custom_placeholder_detail',
          '/custom-placeholders/<int:id>', '/event-sub-topics/<int:event_sub_topic_id>/custom-placeholder')
api.route(CustomPlaceholderRelationship, 'custom_placeholder_event_sub_topic',
          '/custom-placeholders/<int:id>/relationships/event-sub-topic')

# tax
api.route(TaxListPost, 'tax_list_post', '/taxes')
api.route(TaxList, 'tax_list', '/taxes', '/events/<int:event_id>/tax', '/events/<identifier>/tax')
api.route(TaxDetail, 'tax_detail', '/taxes/<int:id>', '/events/<int:event_id>/tax')
api.route(TaxRelationship, 'tax_event', '/taxes/<int:id>/relationships/event')

# event invoices
api.route(EventInvoiceList, 'event_invoice_list', '/event-invoices', '/events/<int:event_id>/event-invoices',
          '/events/<event_identifier>/event-invoices', '/users/<int:user_id>/event-invoices')
api.route(EventInvoiceDetail, 'event_invoice_detail', '/event-invoices/<int:id>')
api.route(EventInvoiceRelationshipRequired, 'event_invoice_user',
          '/event-invoices/<int:id>/relationships/user')
api.route(EventInvoiceRelationshipRequired, 'event_invoice_event',
          '/event-invoices/<int:id>/relationships/event')
api.route(EventInvoiceRelationshipOptional, 'event_invoice_discount_code',
          '/event-invoices/<int:id>/relationships/discount-codes')
api.route(EventInvoiceRelationshipOptional, 'event_invoice_orders',
          '/event-invoices/<int:id>/relationships/orders')

# discount codes
api.route(DiscountCodeListPost, 'discount_code_list_post', '/discount-codes')
api.route(DiscountCodeList, 'discount_code_list', '/events/<int:event_id>/discount-codes',
          '/events/<event_identifier>/discount-codes', '/users/<int:user_id>/discount-codes')
api.route(DiscountCodeDetail, 'discount_code_detail', '/discount-codes/<int:id>',
          '/events/<int:event_id>/discount-code', 'event-invoices/<int:event_invoice_id>/discount-code')
api.route(DiscountCodeRelationshipRequired, 'discount_code_event',
          '/discount-codes/<int:id>/relationships/event')
api.route(DiscountCodeRelationshipOptional, 'discount_code_events',
          '/discount-codes/<int:id>/relationships/events')
api.route(DiscountCodeRelationshipOptional, 'discount_code_user',
          '/discount-codes/<int:id>/relationships/marketer')

# attendees
api.route(AttendeeListPost, 'attendee_list_post', '/attendees')
api.route(AttendeeList, 'attendee_list', '/events/<int:event_id>/attendees',
          '/events/<event_identifier>/attendees', '/orders/<order_identifier>/attendees',
          '/tickets/<int:ticket_id>/attendees', '/users/<int:user_id>/attendees')
api.route(AttendeeDetail, 'attendee_detail', '/attendees/<int:id>')
api.route(AttendeeRelationshipOptional, 'attendee_ticket', '/attendees/<int:id>/relationships/ticket')
api.route(AttendeeRelationshipRequired, 'attendee_event', '/attendees/<int:id>/relationships/event')
api.route(AttendeeRelationshipRequired, 'attendee_order', '/attendees/<int:id>/relationships/order')
api.route(AttendeeRelationshipOptional, 'attendee_user', '/attendees/<int:id>/relationships/user')

# event types
api.route(EventTypeList, 'event_type_list', '/event-types')
api.route(EventTypeDetail, 'event_type_detail', '/event-types/<int:id>', '/events/<int:event_id>/event-type',
          '/events/<event_identifier>/event-type')
api.route(EventTypeRelationship, 'event_type_event', '/event-types/<int:id>/relationships/events')

# event topics
api.route(EventTopicList, 'event_topic_list', '/event-topics')
api.route(EventTopicDetail, 'event_topic_detail', '/event-topics/<int:id>', '/events/<int:event_id>/event-topic',
          '/events/<event_identifier>/event-topic', '/event-sub-topics/<int:event_sub_topic_id>/event-topic')
api.route(EventTopicRelationship, 'event_topic_event',
          '/event-topics/<int:id>/relationships/events')
api.route(EventTopicRelationship, 'event_topic_event_sub_topic',
          '/event-topics/<int:id>/relationships/event-sub-topics')

# event sub topics
api.route(EventSubTopicListPost, 'event_sub_topic_list_post', '/event-sub-topics')
api.route(EventSubTopicList, 'event_sub_topic_list',
          '/event-topics/<int:event_topic_id>/event-sub-topics')
api.route(EventSubTopicDetail, 'event_sub_topic_detail', '/event-sub-topics/<int:id>',
          '/events/<int:event_id>/event-sub-topic',
          '/events/<event_identifier>/event-sub-topic',
          '/custom-placeholders/<int:custom_placeholder_id>/event-sub-topic')
api.route(EventSubTopicRelationshipOptional, 'event_sub_topic_event',
          '/event-sub-topics/<int:id>/relationships/events')
api.route(EventSubTopicRelationshipRequired, 'event_sub_topic_event_topic',
          '/event-sub-topics/<int:id>/relationships/event-topic')
api.route(EventSubTopicRelationshipOptional, 'event_sub_topic_custom_placeholder',
          '/event-sub-topics/<int:id>/relationships/custom-placeholder')

# ticket_fees
api.route(TicketFeeList, 'ticket_fee_list', '/ticket-fees')
api.route(TicketFeeDetail, 'ticket_fee_detail', '/ticket-fees/<int:id>')

# access code
api.route(AccessCodeListPost, 'access_code_list_post', '/access-codes')
api.route(AccessCodeList, 'access_code_list', '/events/<int:event_id>/access-codes',
          '/events/<event_identifier>/access-codes', '/users/<int:user_id>/access-codes',
          '/tickets/<int:ticket_id>/access-codes')
api.route(AccessCodeDetail, 'access_code_detail', '/access-codes/<int:id>')
api.route(AccessCodeRelationshipRequired, 'access_code_event',
          '/access-codes/<int:id>/relationships/event')
api.route(AccessCodeRelationshipOptional, 'access_code_user',
          '/access-codes/<int:id>/relationships/marketer')
api.route(AccessCodeRelationshipOptional, 'access_code_tickets',
          '/access-codes/<int:id>/relationships/tickets')

# activity
api.route(ActivityList, 'activity_list', '/activities')
api.route(ActivityDetail, 'activity_detail', '/activities/<int:id>')

# custom form
api.route(CustomFormListPost, 'custom_form_list_post', '/custom-forms')
api.route(CustomFormList, 'custom_form_list', '/events/<int:event_id>/custom-forms',
          '/events/<event_identifier>/custom-forms')
api.route(CustomFormDetail, 'custom_form_detail', '/custom-forms/<int:id>')
api.route(CustomFormRelationshipRequired, 'custom_form_event',
          '/custom-forms/<int:id>/relationships/event')

# Stripe Authorization API
api.route(StripeAuthorizationListPost, 'stripe_authorization_list_post', '/stripe-authorization')
api.route(StripeAuthorizationList, 'stripe_authorization_list', '/events/<int:event_id>/stripe-authorization',
          '/events/<event_identifier>/stripe-authorization')
api.route(StripeAuthorizationDetail, 'stripe_authorization_detail',  '/stripe-authorization/<int:id>',
          '/events/<int:event_id>/stripe-authorization', '/events/<event_identifier>/stripe-authorization')
api.route(StripeAuthorizationRelationship, 'stripe_authorization_event',
          '/stripe-authorization/<int:id>/relationships/event')


# Orders API
api.route(OrdersListPost, 'order_list_post', '/orders')
api.route(OrdersList, 'orders_list', '/orders', '/events/<int:event_id>/orders',
          '/events/<event_identifier>/orders')
api.route(OrderDetail, 'order_detail', '/orders/<order_identifier>',
          '/attendees/<int:attendee_id>/order')

# Charges API
api.route(ChargeList, 'charge_list', '/orders/<identifier>/charge', '/orders/<order_identifier>/charge')
api.route(OrderRelationship, 'order_attendee', '/orders/<order_identifier>/relationships/attendee')
api.route(OrderRelationship, 'order_ticket', '/orders/<order_identifier>/relationships/ticket')
api.route(OrderRelationship, 'order_user', '/orders/<order_identifier>/relationships/user')
api.route(OrderRelationship, 'order_event', '/orders/<order_identifier>/relationships/event')
api.route(OrderRelationship, 'order_marketer', '/orders/<order_identifier>/relationships/marketer')
api.route(OrderRelationship, 'order_discount', '/orders/<order_identifier>/relationships/discount-code')
api.route(OrderRelationship, 'order_event_invoice', '/orders/<order_identifier>/relationships/event-invoice')

# Event Statistics API
api.route(EventStatisticsGeneralDetail, 'event_statistics_general_detail', '/events/<int:id>/general-statistics',
          '/events/<identifier>/general-statistics')

# Ticket statistics API
api.route(OrderStatisticsEventDetail, 'order_statistics_event_detail', '/events/<int:id>/order-statistics',
          '/events/<identifier>/order-statistics')
api.route(OrderStatisticsTicketDetail, 'order_statistics_ticket_detail', '/tickets/<int:id>/order-statistics')

# Admin Statistics API
api.route(AdminStatisticsSessionDetail, 'admin_statistics_session_detail', '/admin/statistics/sessions')
api.route(AdminStatisticsEventDetail, 'admin_statistics_event_detail', '/admin/statistics/events')
api.route(AdminStatisticsUserDetail, 'admin_statistics_user_detail', '/admin/statistics/users')
api.route(AdminStatisticsMailDetail, 'admin_statistics_mail_detail', '/admin/statistics/mails')
