class OAuth():
    """Google Credentials"""

    CLIENT_ID='449612261522-1eg34prt23l0454et59qgqno3rjd8muq.apps.googleusercontent.com'
    CLIENT_SECRET='aq8XaUlxCfhwwMyZyNw8kS-D'
    REDIRECT_URI='http://localhost:8001/gCallback'
    AUTH_URI='https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URI='https://www.googleapis.com/oauth2/v4/token'
    USER_INFO='https://www.googleapis.com/userinfo/v2/me'
    SCOPE=['profile','email']

class FbOAuth():
	"Facebook Credentials"
	
	CLIENT_ID='1790977354468723'
   	CLIENT_SECRET='830da5c5ab66f0b2224a9ad5efa7cdb4'
   	REDIRECT_URI='http://localhost:8001/fCallback'
   	AUTH_URI='https://www.facebook.com/dialog/oauth'
   	TOKEN_URI='https://graph.facebook.com/oauth/access_token'
   	USER_INFO='https://graph.facebook.com/me?fields=email,id,name,picture'
   	SCOPE=['public_profile','email']
    