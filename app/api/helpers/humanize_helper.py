from datetime import datetime

import humanize
import pytz

def humanize_helper(time):
    """Returns time passed from now in a human readable duration"""

    return humanize.naturaldelta(datetime.now(pytz.utc) 
                - time.astimezone(pytz.utc)) + ' ago'