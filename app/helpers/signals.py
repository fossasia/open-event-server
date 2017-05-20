# Define all your signals here.
# NOTE: Please do not put any signal handlers in this file.
# Each signal handler should remain in the file related to the task its doing, not here.

from blinker import Namespace, Signal
from flask import current_app as app


def new_send(self, *sender, **kwargs):
    """Emit this signal on behalf of *sender*, passing on \*\*kwargs.
    Returns a list of 2-tuples, pairing receivers with their return
    value. The ordering of receiver notification is undefined.
    :param \*sender: Any object or ``None``.  If omitted, synonymous
      with ``None``.  Only accepts one positional argument.
    :param \*\*kwargs: Data to be sent to receivers.
    """
    # Using '*sender' rather than 'sender=None' allows 'sender' to be
    # used as a keyword argument- i.e. it's an invisible name in the
    # function signature.
    if len(sender) == 0:
        sender = None
    elif len(sender) > 1:
        raise TypeError('send() accepts only one positional argument, '
                        '%s given' % len(sender))
    else:
        sender = sender[0]
    if not self.receivers or app.config['TESTING']:
        return []
    else:
        return [(receiver, receiver(sender, **kwargs))
                for receiver in self.receivers_for(sender)]

Signal.send = new_send

event_signals = Namespace()

event_json_modified = event_signals.signal('event_json_modified')
speakers_modified = event_signals.signal('speakers_modified')
sessions_modified = event_signals.signal('sessions_modified')
microlocations_modified = event_signals.signal('microlocations_modified')
