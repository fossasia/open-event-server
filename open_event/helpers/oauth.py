from flask import request
from urlparse import urlparse

from open_event.settings import get_settings


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
    Fb_USER_INFO = 'https://graph.facebook.com/me?fields=email,id,name,picture'
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


class InstagramOAuth(object):
    INSTAGRAM_OAUTH_URI = "https://api.instagram.com/oauth/authorize/"
    SCOPE = ['basic', 'public_content ']
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
