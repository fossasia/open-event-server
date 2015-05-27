import os
_basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
# SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'] # heroku
# DATABASE_CONNECT_OPTIONS = {}
#
# THREADS_PER_PAGE = 8
#
# CSRF_ENABLED = True
# CSRF_SESSION_KEY = "somethingimpossibletoguess"
#
# RECAPTCHA_USE_SSL = False
# RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
# RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
# RECAPTCHA_OPTIONS = {'theme': 'white'}