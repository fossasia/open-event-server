# Define all your signals here.
# NOTE: Please do not put any signal handlers in this file.
# Each signal handler should remain in the file related to the task its doing, not here.

from blinker import Namespace

event_signals = Namespace()

event_json_modified = event_signals.signal('event_json_modified')
speakers_modified = event_signals.signal('speakers_modified')
sessions_modified = event_signals.signal('sessions_modified')
microlocations_modified = event_signals.signal('microlocations_modified')
