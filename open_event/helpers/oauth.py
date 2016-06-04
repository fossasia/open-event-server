class OAuth(object):
    """Google Credentials"""

    CLIENT_ID = '449612261522-1eg34prt23l0454et59qgqno3rjd8muq.apps.googleusercontent.com'
    CLIENT_SECRET = 'aq8XaUlxCfhwwMyZyNw8kS-D'
    REDIRECT_URI = 'http://localhost:8001/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']

    @classmethod
    def get_client_id(self):
        return self.CLIENT_ID

    @classmethod
    def get_client_secret(self):
        return self.CLIENT_SECRET

    @classmethod
    def get_redirect_uri(self):
        return self.REDIRECT_URI

    @classmethod
    def get_auth_uri(self):
        return self.AUTH_URI

    @classmethod
    def get_token_uri(self):
        return self.TOKEN_URI

    @classmethod
    def get_user_info(self):
        return self.USER_INFO


class FbOAuth(object):
    """Facebook Credentials"""

    Fb_CLIENT_ID = '1790977354468723'
    Fb_CLIENT_SECRET = '830da5c5ab66f0b2224a9ad5efa7cdb4'
    Fb_REDIRECT_URI = 'http://localhost:8001/fCallback'
    Fb_AUTH_URI = 'https://www.facebook.com/dialog/oauth'
    Fb_TOKEN_URI = 'https://graph.facebook.com/oauth/access_token'
    Fb_USER_INFO = 'https://graph.facebook.com/me?fields=email,id,name,picture'
    SCOPE = ['public_profile', 'email']

    @classmethod
    def get_client_id(self):
        return self.Fb_CLIENT_ID

    @classmethod
    def get_client_secret(self):
        return self.Fb_CLIENT_SECRET

    @classmethod
    def get_redirect_uri(self):
        return self.Fb_REDIRECT_URI

    @classmethod
    def get_auth_uri(self):
        return self.Fb_AUTH_URI

    @classmethod
    def get_token_uri(self):
        return self.Fb_TOKEN_URI

    @classmethod
    def get_user_info(self):
        return self.Fb_USER_INFO
