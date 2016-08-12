from flask import request
from urlparse import urlparse
import oauth2
from app.settings import get_settings


class OAuth(object):
    """Google Credentials"""

    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']

    @classmethod
    def get_client_id(self):
        return get_settings()['google_client_id']

    @classmethod
    def get_client_secret(self):
        return get_settings()['google_client_secret']

    @classmethod
    def get_redirect_uri(self):
        url = urlparse(request.url)
        redirect_uri = url.scheme + '://' + url.netloc + '/gCallback'
        return redirect_uri

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
    Fb_AUTH_URI = 'https://www.facebook.com/dialog/oauth'
    Fb_TOKEN_URI = 'https://graph.facebook.com/oauth/access_token'
    Fb_USER_INFO = 'https://graph.facebook.com/me?fields=email,id,name,picture,bio,last_name,first_name,link'
    SCOPE = ['public_profile', 'email']

    @classmethod
    def get_client_id(self):
        return get_settings()['fb_client_id']

    @classmethod
    def get_client_secret(self):
        return get_settings()['fb_client_secret']

    @classmethod
    def get_redirect_uri(self):
        url = urlparse(request.url)
        fb_redirect_uri = url.scheme + '://' + url.netloc + '/fCallback'
        return fb_redirect_uri

    @classmethod
    def get_auth_uri(self):
        return self.Fb_AUTH_URI

    @classmethod
    def get_token_uri(self):
        return self.Fb_TOKEN_URI

    @classmethod
    def get_user_info(self):
        return self.Fb_USER_INFO


class TwitterOAuth(object):
    """Facebook Credentials"""
    TW_AUTH_URI = 'https://api.twitter.com/oauth/authorize'
    TW_REQUEST_TOKEN_URI = 'https://api.twitter.com/oauth/request_token'
    TW_ACCESS_TOKEN = "https://api.twitter.com/oauth/access_token?"

    @classmethod
    def get_client_id(self):
        return get_settings()['tw_consumer_key']

    @classmethod
    def get_client_secret(self):
        return get_settings()['tw_consumer_secret']

    @classmethod
    def get_redirect_uri(self):
        url = urlparse(request.url)
        tw_redirect_uri = url.scheme + '://' + url.netloc + '/tCallback'
        return tw_redirect_uri

    def get_consumer(self):
        return oauth2.Consumer(key=self.get_client_id(),
                               secret=self.get_client_secret())

    def get_request_token(self):
        client = oauth2.Client(self.get_consumer())
        return client.request(self.TW_REQUEST_TOKEN_URI, "GET")

    def get_access_token(self, oauth_verifier, oauth_token):
        consumer = self.get_consumer()
        client = oauth2.Client(consumer)
        return client.request(
            self.TW_ACCESS_TOKEN + 'oauth_verifier=' + oauth_verifier + "&oauth_token=" + oauth_token, "POST")

    def get_authorized_client(self, oauth_verifier, oauth_token):
        import urlparse
        resp, content = self.get_access_token(oauth_verifier, oauth_token)
        access_token = dict(urlparse.parse_qsl(content))
        token = oauth2.Token(access_token["oauth_token"], access_token["oauth_token_secret"])
        token.set_verifier(oauth_verifier)
        return oauth2.Client(self.get_consumer(), token), access_token


class InstagramOAuth(object):
    INSTAGRAM_OAUTH_URI = "https://api.instagram.com/oauth/authorize/"
    INSTAGRAM_TOKEN_URI = "https://api.instagram.com/oauth/access_token"
    SCOPE = ['basic', 'public_content']
    @classmethod
    def get_client_id(self):
        return get_settings()['in_client_id']

    @classmethod
    def get_client_secret(self):
        return get_settings()['in_client_secret']

    @classmethod
    def get_redirect_uri(self):
        url = urlparse(request.url)
        i_redirect_uri = url.scheme + '://' + url.netloc + '/iCallback'
        return i_redirect_uri

    @classmethod
    def get_auth_uri(self):
        return self.INSTAGRAM_OAUTH_URI

    @classmethod
    def get_token_uri(self):
        return self.INSTAGRAM_TOKEN_URI
