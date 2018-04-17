import sys


def u(string):
    if sys.version_info[0] >= 3:
        return str(string)
    else:
        return unicode(string)
