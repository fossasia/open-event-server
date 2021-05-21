"""
All the System mails
Register a mail here before using it
"""


class MailType:
    USER_REGISTER = 'user_registration'
    USER_CONFIRM = 'user_confirmation'
    USER_CHANGE_EMAIL = 'user_change_email'
    NEW_SESSION = 'new_session'
    PASSWORD_RESET = 'password_reset'
    PASSWORD_CHANGE = 'password_change'
    PASSWORD_RESET_AND_VERIFY = 'password_reset_verify'
    EVENT_ROLE = 'event_role'
    GROUP_ROLE = 'group_role'
    SESSION_STATE_CHANGE = 'session_state_change'
    TICKET_PURCHASED = 'ticket_purchased'
    TICKET_PURCHASED_ATTENDEE = 'ticket_purchased_attendee'
    TICKET_PURCHASED_ORGANIZER = 'ticket_purchased_organizer'
    TICKET_CANCELLED = 'ticket_cancelled'
    # TICKET_CANCELLED_ORGANIZER = 'ticket_cancelled_organizer' # To be implemented
    # TICKET_RESEND_ORGANIZER = 'ticket_resend_organizer' # To be implemented
    EVENT_EXPORTED = 'event_exported'
    EVENT_EXPORT_FAIL = 'event_export_fail'
    EVENT_IMPORTED = 'event_imported'
    EVENT_IMPORT_FAIL = 'event_import_fail'
    MONTHLY_PAYMENT = 'monthly_payment'
    MONTHLY_PAYMENT_FOLLOWUP = 'monthly_payment_follow_up'
    MONTHLY_PAYMENT_PRE_DUE = 'monthly_payment_pre_due'
    MONTHLY_PAYMENT_POST_DUE = 'monthly_payment_post_due'
    TEST_MAIL = 'test_mail'
    CONTACT_ORGANIZERS = 'contact_organizers'
    VIDEO_MODERATOR_INVITE = "video_moderator_invite"

    @staticmethod
    def entries():
        # Extract all values of defined entries after filtering internal keys
        return list(
            map(
                lambda entry: entry[1],
                filter(
                    lambda entry: not entry[0].startswith('__') and type(entry[1]) == str,
                    MailType.__dict__.items(),
                ),
            )
        )


MAILS = {
    MailType.SESSION_STATE_CHANGE: {
        'recipient': 'Speaker',
        'pending': {
            'subject': 'Your speaker submission for {event_name} titled {session_name}',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "We have received your submission {session_name} for {event_name}<br/><br/>"
            "Your proposal will be reviewed by the event organizers and review team. The current status of your session is now \"Pending\".<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'accepted': {
            'subject': 'Accepted! Congratulations Your submission for {event_name} titled {session_name} has been Accepted',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Your session status for the submission {session_name} for {event_name} was changed to \"Accepted\". Congratulations!<br/><br/>"
            "Your proposal will be scheduled by the event organizers and review team. Please (re)confirm your participation with the organizers of the event, if required.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'confirmed': {
            'subject': 'Confirmed! Congratulations Your submission for {event_name} titled {session_name} has been Confirmed',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Your session status for the submission {session_name} for {event_name} was changed to \"Confirmed\". Congratulations!<br/><br/>"
            "Your proposal will be scheduled by the event organizers and review team. Please inform the event organizers in case there are any changes to your participation.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'rejected': {
            'subject': 'Not Accepted. Your submission for {event_name} titled {session_name} was not accepted',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Unfortunately your submission {session_name} for {event_name} was not accepted. Your session status was changed to \"Rejected\".<br/><br/>"
            "The status change was done by event organizers. If there are questions about this change please contact the organizers.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'canceled': {
            'subject': 'Canceled! Your submission for {event_name} titled {session_name} has been Canceled',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Your session status for the submission {session_name} for {event_name} was changed to \"Canceled\".<br/><br/>"
            "The status change was done by event organizers. If there are questions about this change please contact the organizers.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'withdrawn': {
            'subject': 'Withdrawn! Your submission for {event_name} titled {session_name} has been Withdrawn',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Your session status for the submission {session_name} for {event_name} was changed to \"Withdrawn\".<br/><br/>"
            "The status change was done by event organizers. If there are questions about this change please contact the organizers.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
    },
    MailType.NEW_SESSION: {
        'recipient': 'Owner, Organizer',
        'subject': 'New session proposal for {session.event.name} titled {session.title}',
        'template': 'email/new_session.html',
    },
    MailType.USER_REGISTER: {
        'recipient': 'User',
        'subject': 'Welcome to {app_name}. Please verify your account',
        'template': 'email/user_register.html',
    },
    MailType.USER_CONFIRM: {
        'recipient': 'User',
        'subject': 'Email Confirmation to Create Account for Open-Event',
        'template': 'email/user_confirm.html',
    },
    MailType.USER_CHANGE_EMAIL: {
        'recipient': 'User',
        'subject': 'Your email has been already changed',
        'template': 'email/user_change_email.html',
    },
    MailType.PASSWORD_RESET: {
        'recipient': 'User',
        'subject': '{app_name}: Password Reset',
        'template': 'email/password_reset.html',
    },
    MailType.PASSWORD_RESET_AND_VERIFY: {
        'recipient': 'User',
        'subject': '{app_name}: Reset your password and verify your account',
        'template': 'email/password_reset_and_verify.html',
    },
    MailType.PASSWORD_CHANGE: {
        'recipient': 'User',
        'subject': '{app_name}: Password Change',
        'template': 'email/password_change.html',
    },
    MailType.EVENT_ROLE: {
        'recipient': 'User',
        'subject': 'Invitation to be {role} at Event: {event}',
        'template': 'email/event_role.html',
    },
    MailType.GROUP_ROLE: {
        'recipient': 'User',
        'subject': 'Invitation to be {role} at Group: {group}',
        'template': 'email/group_role.html',
    },
    MailType.TICKET_PURCHASED: {
        'recipient': 'User',
        'subject': 'Your order invoice and tickets for {event_name} ({invoice_id}) ',
        'template': 'email/ticket_purchased.html',
    },
    MailType.TICKET_PURCHASED_ATTENDEE: {
        'recipient': 'Attendee',
        'subject': 'Your tickets for {event_name} ({invoice_id}) ',
        'template': 'email/ticket_purchased_attendee.html',
    },
    MailType.TICKET_PURCHASED_ORGANIZER: {
        'recipient': 'Owner, Organizer, Coorganizer',
        'subject': 'New ticket purchase for {event_name} by {buyer_email} ({invoice_id}) ',
        'template': 'email/ticket_purchased_organizer.html',
    },
    MailType.TICKET_CANCELLED: {
        'recipient': 'User',
        'subject': 'Your order for {event_name} has been cancelled ({invoice_id})',
        'template': 'email/ticket_cancelled.html',
    },
    MailType.EVENT_EXPORTED: {
        'recipient': 'User',
        'subject': 'Event {event_name} has been exported',
        'template': 'email/event_exported.html',
    },
    MailType.EVENT_EXPORT_FAIL: {
        'recipient': 'User',
        'subject': 'Export of event {event_name} failed',
        'template': 'email/event_export_fail.html',
    },
    MailType.MONTHLY_PAYMENT: {
        'recipient': 'Owner',
        'subject': 'Your invoice for {event_name} for {date} is available on {app_name}',
        'sent_at': '1st day of the month',
        'template': 'email/monthly_payment_email.html',
    },
    MailType.MONTHLY_PAYMENT_FOLLOWUP: {
        'recipient': 'Owner',
        'subject': 'Reminder: Your invoice for {event_name} for {date} is available on {app_name}',
        'sent_at': '15th day of the month',
        'template': 'email/monthly_payment_followup_email.html',
    },
    MailType.MONTHLY_PAYMENT_PRE_DUE: {
        'recipient': 'Owner',
        'subject': 'Reminder: Your invoice for {event_name} for {date} is available on {app_name}',
        'sent_at': '27th day of the month',
        'template': 'email/monthly_payment_pre_due_email.html',
    },
    MailType.MONTHLY_PAYMENT_POST_DUE: {
        'recipient': 'Owner',
        'subject': 'Please pay your overdue invoice for {event_name} for {date} on {app_name}',
        'sent_at': '30th day of the month',
        'template': 'email/monthly_payment_post_due_email.html',
    },
    MailType.EVENT_IMPORTED: {
        'recipient': 'User',
        'subject': 'Event {event_name} has been imported',
        'template': 'email/event_imported.html',
    },
    MailType.EVENT_IMPORT_FAIL: {
        'recipient': 'User',
        'subject': 'Import of event failed',
        'template': 'email/event_import_fail.html',
    },
    MailType.CONTACT_ORGANIZERS: {
        'recipient': 'Owner, Organizer',
        'template': 'email/organizer_contact_attendee.html',
    },
    MailType.TEST_MAIL: {
        'recipient': 'User',
        'subject': 'Test Mail Subject',
        'message': ("This is a  <strong> Test </strong> E-mail."),
    },
    MailType.VIDEO_MODERATOR_INVITE: {
        'recipient': 'User',
        'subject': 'Video Moderator of video {video_name} at event {event_name}',
        'template': 'email/video_stream_moderator.html',
    },
}
