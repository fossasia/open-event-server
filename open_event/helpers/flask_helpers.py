from flask import request
from jinja2 import Undefined

def get_real_ip():
    try:
        if 'X-Forwarded-For' in request.headers:
            return request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
        else:
            return request.remote_addr or 'untrackable'
    except:
        return 'untrackable'

class SilentUndefined(Undefined):
    """
    From http://stackoverflow.com/questions/6190348/
    Don't break page loads because vars aren't there!
    """
    def _fail_with_undefined_error(self, *args, **kwargs):
        return False
    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __call__ = \
        __getitem__ = __lt__ = __le__ = __gt__ = __ge__ = __int__ = \
        __float__ = __complex__ = __pow__ = __rpow__ = \
        _fail_with_undefined_error

