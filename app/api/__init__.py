from app.api.bootstrap import api
from app.api.ticket_fees import TicketFeeList, TicketFeeDetail
from app.api.users import UserList, UserDetail, UserRelationship
from app.api.notifications import NotificationList, NotificationDetail, NotificationRelationship
from app.api.tickets import TicketList, TicketDetail, TicketRelationship
from app.api.events import EventList, EventDetail, EventRelationship
from app.api.event_types import EventTypeList, EventTypeDetail, EventTypeRelationship
from app.api.event_topics import EventTopicList, EventTopicDetail, EventTopicRelationship
from app.api.event_sub_topics import EventSubTopicList, EventSubTopicDetail, EventSubTopicRelationship
from app.api.microlocations import MicrolocationList, MicrolocationDetail, MicrolocationRelationship
from app.api.sessions import SessionList, SessionDetail, SessionRelationship
from app.api.social_links import SocialLinkList, SocialLinkDetail, SocialLinkRelationship
from app.api.sponsors import SponsorList, SponsorDetail, SponsorRelationship
from app.api.tracks import TrackList, TrackDetail, TrackRelationship
from app.api.speakers_calls import SpeakersCallList, SpeakersCallDetail, SpeakersCallRelationship
from app.api.event_invoices import EventInvoiceList, EventInvoiceDetail, EventInvoiceRelationship
from app.api.role_invites import RoleInviteList, RoleInviteDetail, RoleInviteRelationship
from app.api.users_events_roles import UsersEventsRolesList, UsersEventsRolesDetail, UsersEventsRolesRelationship
from app.api.image_sizes import ImageSizeList, ImageSizeDetail
from app.api.roles import RoleList, RoleDetail
from app.api.session_types import SessionTypeList, SessionTypeDetail, SessionTypeRelationship
from app.api.event_copyright import EventCopyrightList, EventCopyrightDetail, EventCopyrightRelationship
from app.api.pages import PageList, PageDetail
from app.api.tax import TaxList, TaxDetail, TaxRelationship
from app.api.settings import SettingDetail
from app.api.discount_codes import DiscountCodeList, DiscountCodeDetail, DiscountCodeRelationship
from app.api.ticket_tags import TicketTagList, TicketTagDetail, TicketTagRelationship
from app.api.attendees import AttendeeList, AttendeeDetail, AttendeeRelationship
from app.api.modules import ModuleDetail

# users
api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>', '/notifications/<int:notification_id>/user',
          '/event-invoices/<int:event_invoice_id>/user', '/users-events-roles/<int:users_events_role_id>/user')
api.route(UserRelationship, 'user_notification', '/users/<int:id>/relationships/notifications')
api.route(UserRelationship, 'user_event_invoices', '/users/<int:id>/relationships/event-invoices')

# notifications
api.route(NotificationList, 'notification_list', '/users/<int:id>/notifications')
api.route(NotificationDetail, 'notification_detail', '/notifications/<int:id>')
api.route(NotificationRelationship, 'notification_user',
          '/notifications/<int:id>/relationships/user')

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

# roles
api.route(RoleList, 'role_list', '/roles')
api.route(RoleDetail, 'role_detail', '/roles/<int:id>', '/role-invites/<int:role_invite_id>/role',
          '/users-events-roles/<int:users_events_role_id>/role')

# role_invites
api.route(RoleInviteList, 'role_invite_list', '/events/<int:event_id>/role-invites',
          '/events/<event_identifier>/role-invites')
api.route(RoleInviteDetail, 'role_invite_detail', '/role-invites/<int:id>')
api.route(RoleInviteRelationship, 'role_invite_event', '/role-invites/<int:id>/relationships/event')
api.route(RoleInviteRelationship, 'role_invite_role', '/role-invites/<int:id>/relationships/role')

# users_events_roles
api.route(UsersEventsRolesList, 'users_events_role_list', '/events/<int:event_id>/users-events-roles',
          '/events/<event_identifier>/users-events-roles')
api.route(UsersEventsRolesDetail, 'users_events_role_detail', '/users-events-roles/<int:id>')
api.route(UsersEventsRolesRelationship, 'users_events_role_event', '/users-events-roles/<int:id>/relationships/event')
api.route(UsersEventsRolesRelationship, 'users_events_role_role', '/users-events-roles/<int:id>/relationships/role')
api.route(UsersEventsRolesRelationship, 'users_events_role_user', '/users-events-roles/<int:id>/relationships/user')

# tickets
api.route(TicketList, 'ticket_list', '/events/<int:event_id>/tickets',
          '/events/<event_identifier>/tickets', '/ticket-tags/<int:ticket_tag_id>/tickets')
api.route(TicketDetail, 'ticket_detail', '/tickets/<int:id>', '/attendees/<int:attendee_id>/ticket')
api.route(TicketRelationship, 'ticket_event', '/tickets/<int:id>/relationships/event')
api.route(TicketRelationship, 'ticket_ticket_tag', '/tickets/<int:id>/relationships/ticket-tags')

# ticket_tags
api.route(TicketTagList, 'ticket_tag_list', '/tickets/<int:ticket_id>/ticket-tags',
          '/events/<int:event_id>/ticket-tags', '/events/<event_identifier>/ticket-tags')
api.route(TicketTagDetail, 'ticket_tag_detail', '/ticket-tags/<int:id>')
api.route(TicketTagRelationship, 'ticket_tag_ticket', '/ticket-tags/<int:id>/relationships/tickets')
api.route(TicketTagRelationship, 'ticket_tag_event', '/ticket-tags/<int:id>/relationships/event')

# events
api.route(EventList, 'event_list', '/events', '/event-types/<int:event_type_id>/events',
          '/event-topics/<int:event_topic_id>/events',
          '/event-sub-topics/<int:event_sub_topic_id>/events', '/discount-codes/<int:discount_code_id>/events')
api.route(EventDetail, 'event_detail', '/events/<int:id>', '/events/<identifier>',
          '/tickets/<int:ticket_id>/event', '/microlocations/<int:microlocation_id>/event',
          '/social-links/<int:social_link_id>/event',
          '/sponsors/<int:sponsor_id>/event', '/tracks/<int:track_id>/event',
          '/speakers-calls/<int:speakers_call_id>/event', '/session-types/<int:session_type_id>/event',
          '/event-copyright/<int:copyright_id>/event', '/tax/<int:tax_id>/event',
          '/event-invoices/<int:event_invoice_id>/event', '/discount-codes/<int:discount_code_id>/event',
          '/sessions/<int:session_id>/event', '/ticket-tags/<int:ticket_tag_id>/event',
          '/role-invites/<int:role_invite_id>/event', '/users-events-roles/<int:users_events_role_id>/event')
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
api.route(EventRelationship, 'event_users_events_role', '/events/<int:id>/relationships/users-events-roles',
          '/events/<identifier>/relationships/users-events-roles')

# microlocations
api.route(MicrolocationList, 'microlocation_list', '/microlocations', '/events/<int:event_id>/microlocations',
          '/events/<event_identifier>/microlocations')
api.route(MicrolocationDetail, 'microlocation_detail', '/microlocations/<int:id>',
          '/sessions/<int:session_id>/microlocation')
api.route(MicrolocationRelationship, 'microlocation_session',
          '/microlocations/<int:id>/relationships/sessions')
api.route(MicrolocationRelationship, 'microlocation_event',
          '/microlocations/<int:id>/relationships/event')

# sessions
api.route(SessionList, 'session_list', '/sessions', '/events/<int:event_id>/sessions',
          '/events/<event_identifier>/sessions',
          '/tracks/<int:track_id>/sessions', '/session_types/<int:session_type_id>/sessions',
          '/microlocations/<int:microlocation_id>/sessions')
api.route(SessionDetail, 'session_detail', '/sessions/<int:id>')
api.route(SessionRelationship, 'session_microlocation',
          '/sessions/<int:id>/relationships/microlocation')
api.route(SessionRelationship, 'session_track', '/sessions/<int:id>/relationships/track')
api.route(SessionRelationship, 'session_session_type',
          '/sessions/<int:id>/relationships/session-type')
api.route(SessionRelationship, 'session_event',
          '/sessions/<int:id>/relationships/event')

# social_links
api.route(SocialLinkList, 'social_link_list', '/events/<int:event_id>/social-links',
          '/events/<event_identifier>/social-links')
api.route(SocialLinkDetail, 'social_link_detail', '/social-links/<int:id>')
api.route(SocialLinkRelationship, 'social_link_event',
          '/social-links/<int:id>/relationships/event')

# sponsors
api.route(SponsorList, 'sponsor_list', '/sponsors', '/events/<int:event_id>/sponsors',
          '/events/<event_identifier>/sponsors')
api.route(SponsorDetail, 'sponsor_detail', '/sponsors/<int:id>')
api.route(SponsorRelationship, 'sponsor_event', '/sponsors/<int:id>/relationships/event')

# tracks
api.route(TrackList, 'track_list', '/events/<int:event_id>/tracks',
          '/events/<event_identifier>/tracks')
api.route(TrackDetail, 'track_detail', '/tracks/<int:id>', '/sessions/<int:session_id>/track')
api.route(TrackRelationship, 'track_sessions', '/tracks/<int:id>/relationships/sessions')
api.route(TrackRelationship, 'track_event', '/tracks/<int:id>/relationships/event')

# speakers_calls
api.route(SpeakersCallList, 'speakers_call_list', '/events/<int:event_id>/speakers-call',
          '/events/<event_identifier>/speakers-call')
api.route(SpeakersCallDetail, 'speakers_call_detail', '/speakers-calls/<int:id>',
          '/events/<int:event_id>/speakers-call', '/events/<event_identifier>/speakers-call')
api.route(SpeakersCallRelationship, 'speakers_call_event',
          '/speakers-calls/<int:id>/relationships/event')

# session_types
api.route(SessionTypeList, 'session_type_list', '/events/<int:event_id>/session-types',
          '/events/<event_identifier>/session-types')
api.route(SessionTypeDetail, 'session_type_detail', '/session-types/<int:id>',
          '/sessions/<int:session_id>/session-type')
api.route(SessionTypeRelationship, 'session_type_sessions',
          '/session-types/<int:id>/relationships/sessions')
api.route(SessionTypeRelationship, 'session_type_event',
          '/session-types/<int:id>/relationships/event')

# event_copyright
api.route(EventCopyrightList, 'event_copyright_list', '/events/<int:event_id>/event-copyright',
          '/events/<event_identifier>/event-copyright')
api.route(EventCopyrightDetail, 'event_copyright_detail',
          '/event-copyright/<int:id>', '/events/<int:event_id>/event-copyright',
          '/events/<event_identifier>/event-copyright')
api.route(EventCopyrightRelationship, 'copyright_event',
          '/event-copyright/<int:id>/relationships/event')

# tax
api.route(TaxList, 'tax_list', '/events/<int:event_id>/tax', '/events/<identifier>/tax')
api.route(TaxDetail, 'tax_detail', '/tax/<int:id>', '/events/<int:event_id>/tax')
api.route(TaxRelationship, 'tax_event', '/tax/<int:id>/relationships/event')

# event invoices
api.route(EventInvoiceList, 'event_invoice_list', '/events/<int:event_id>/event-invoices',
          '/events/<event_identifier>/event-invoices', '/users/<int:user_id>/event-invoices')
api.route(EventInvoiceDetail, 'event_invoice_detail', '/event-invoices/<int:id>')
api.route(EventInvoiceRelationship, 'event_invoice_user',
          '/event-invoices/<int:id>/relationships/user')
api.route(EventInvoiceRelationship, 'event_invoice_event',
          '/event-invoices/<int:id>/relationships/event')
api.route(EventInvoiceRelationship, 'event_invoice_discount_code',
          '/event-invoices/<int:id>/relationships/discount-codes')

# discount codes
api.route(DiscountCodeList, 'discount_code_list', '/discount-codes', '/events/<int:event_id>/discount-codes',
          '/events/<event_identifier>/discount-codes')
api.route(DiscountCodeDetail, 'discount_code_detail', '/discount-codes/<int:id>',
          'event-invoices/<int:event_invoice_id>/discount-code')
api.route(DiscountCodeRelationship, 'discount_code_event',
          '/discount-codes/<int:id>/relationships/event')
api.route(DiscountCodeRelationship, 'discount_code_events',
          '/discount-codes/<int:id>/relationships/events')

# attendees
api.route(AttendeeList, 'attendee_list', '/attendees',
          '/orders/<int:order_id>/tickets/<int:ticket_id>/attendees')
api.route(AttendeeDetail, 'attendee_detail', '/attendees/<int:id>')
api.route(AttendeeRelationship, 'attendee_ticket', '/attendees/<int:id>/relationships/ticket')

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
api.route(EventSubTopicList, 'event_sub_topic_list',
          '/event-topics/<int:event_topic_id>/event-sub-topics')
api.route(EventSubTopicDetail, 'event_sub_topic_detail', '/event-sub-topics/<int:id>',
          '/events/<int:event_id>/event-sub-topic',
          '/events/<event_identifier>/event-sub-topic')
api.route(EventSubTopicRelationship, 'event_sub_topic_event',
          '/event-sub-topics/<int:id>/relationships/events')
api.route(EventSubTopicRelationship, 'event_sub_topic_event_topic',
          '/event-sub-topics/<int:id>/relationships/event-topic')
# ticket_fees
api.route(TicketFeeList, 'ticket_fee_list', '/ticket-fees')
api.route(TicketFeeDetail, 'ticket_fee_detail', '/ticket-fees/<int:id>')
