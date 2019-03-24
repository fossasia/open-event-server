import urllib

import oauth2
from flask import request

from app.settings import get_settings
from app.api.helpers.files import make_frontend_url


class GoogleOAuth(object):
    """Google Credentials"""

    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']

    @classmethod
    def get_client_id(cls):
        return get_settings()['google_client_id']

    @classmethod
    def get_client_secret(cls):
        return get_settings()['google_client_secret']

    @classmethod
    def get_redirect_uri(cls):
        url = urllib.parse.urlparse(request.url)
        redirect_uri = url.scheme + '://' + url.netloc + '/gCallback'
        return redirect_uri

    @classmethod
    def get_auth_uri(cls):
        return cls.AUTH_URI

    @classmethod
    def get_token_uri(cls):
        return cls.TOKEN_URI

    @classmethod
    def get_user_info(cls):
        return cls.USER_INFO


class FbOAuth(object):
    """Facebook Credentials"""
    Fb_AUTH_URI = 'https://www.facebook.com/dialog/oauth'
    Fb_TOKEN_URI = 'https://graph.facebook.com/oauth/access_token'
    Fb_USER_INFO = 'https://graph.facebook.com/me?fields=' +\
        'email,id,name,picture,last_name,first_name,link'
    SCOPE = ['public_profile', 'email']

    @classmethod
    def get_client_id(cls):
        return get_settings()['fb_client_id']

    @classmethod
    def get_client_secret(cls):
        return get_settings()['fb_client_secret']

    @classmethod
    def get_redirect_uri(cls):
        url = make_frontend_url(
            '/oauth/callback?provider=facebook')
        return url

    @classmethod
    def get_auth_uri(cls):
        return cls.Fb_AUTH_URI

    @classmethod
    def get_token_uri(cls):
        return cls.Fb_TOKEN_URI

    @classmethod
    def get_user_info(cls):
        return cls.Fb_USER_INFO


class TwitterOAuth(object):
    """Twitter Credentials"""
    TW_AUTH_URI = 'https://api.twitter.com/oauth/authorize'
    TW_REQUEST_TOKEN_URI = 'https://api.twitter.com/oauth/request_token'
    TW_ACCESS_TOKEN = "https://api.twitter.com/oauth/access_token"

    @classmethod
    def get_client_id(cls):
        return get_settings()['tw_consumer_key']

    @classmethod
    def get_client_secret(cls):
        return get_settings()['tw_consumer_secret']

    @classmethod
    def get_token_uri(cls):
        return cls.TW_REQUEST_TOKEN_URI

    @classmethod
    def get_redirect_uri(cls):
        url = urllib.parse.urlparse(request.url)
        tw_redirect_uri = url.scheme + '://' + url.netloc + '/tCallback'
        return tw_redirect_uri

    def get_consumer(self):
        return oauth2.Consumer(key=self.get_client_id(),
                               secret=self.get_client_secret())

    def get_auth_uri(cls):
        return cls.TW_AUTH_URI

    def get_access_token(self, oauth_verifier, oauth_token):
        consumer = self.get_consumer()
        client = oauth2.Client(consumer)
        return client.request(
            self.TW_ACCESS_TOKEN + 'oauth_verifier=' +
            oauth_verifier + "&oauth_token=" + oauth_token, "POST"
        )

    def get_authorized_client(self, oauth_verifier, oauth_token):
        resp, content = self.get_access_token(oauth_verifier, oauth_token)
        access_token = dict(urllib.parse.urlparse.parse_qsl(content))
        token = oauth2.Token(
            access_token["oauth_token"], access_token["oauth_token_secret"]
        )
        token.set_verifier(oauth_verifier)
        return oauth2.Client(self.get_consumer(), token), access_token


class InstagramOAuth(object):
    """Instagram Credentials"""
    INSTAGRAM_OAUTH_URI = "https://api.instagram.com/oauth/authorize/"
    INSTAGRAM_TOKEN_URI = "https://api.instagram.com/oauth/access_token"
    SCOPE = ['basic', 'public_content']

    @classmethod
    def get_client_id(cls):
        return get_settings()['in_client_id']

    @classmethod
    def get_client_secret(cls):
        return get_settings()['in_client_secret']

    @classmethod
    def get_redirect_uri(cls):
        url = urllib.parse.urlparse(request.url)
        i_redirect_uri = url.scheme + '://' + url.netloc + '/iCallback'
        return i_redirect_uri

    @classmethod
    def get_auth_uri(cls):
        return cls.INSTAGRAM_OAUTH_URI

    @classmethod
    def get_token_uri(cls):
        return cls.INSTAGRAM_TOKEN_URI
