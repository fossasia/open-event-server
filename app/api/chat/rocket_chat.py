import logging

import requests

from app.api.helpers.db import get_new_identifier, get_or_create
from app.models import db
from app.models.event import Event
from app.models.setting import Setting
from app.models.user import User
from app.settings import get_settings

logger = logging.getLogger(__name__)


class RocketChatException(ValueError):
    class CODES:
        DISABLED = 'integration_disabled'
        UNHANDLED = 'unhandled'

    code = None
    response = None

    def __init__(self, message, code=CODES.UNHANDLED, response=None) -> None:
        self.code = code
        self.response = response
        super().__init__(message)


def login(
    user: User, event: Event, method='login', login_url='', api_url='', is_bot=False
):
    def save_token(token):
        user.rocket_chat_token = token
        db.session.add(user)
        db.session.commit()

    res = requests.post(
        login_url, json=dict(email=user.email, password=user.rocket_chat_password)
    )
    data = res.json()
    if res.status_code == 200:
        token = data['data']['authToken']
        save_token(token)
        if not is_bot:
            if event.chat_room_id:
                add_in_room(event, data['data']['userId'], api_url, login_url)
            else:
                create_room(event, data['data']['userId'], api_url, login_url)
        return dict(method=method, token=token, res=data)
    else:
        # Unhandled Case
        logger.error('Error while rocket chat login: %s', data)
        raise RocketChatException('Error while logging in', response=res)


def register(
    user: User,
    event: Event,
    api_url='',
    login_url='',
    username_suffix='',
    is_bot: bool = False,
):
    settings = get_settings()
    register_url = api_url + '/api/v1/users.register'
    register_data = {
        'name': user.public_name or user.full_name,
        'email': user.email,
        'pass': user.rocket_chat_password,
        'username': user.rocket_chat_username + username_suffix,
    }
    if registration_secret := settings['rocket_chat_registration_secret']:
        register_data['secretURL'] = registration_secret

    res = requests.post(register_url, json=register_data)

    data = res.json()
    if res.status_code == 200:
        return login(user, event, 'registered', login_url, api_url, is_bot)
    elif res.status_code == 400:
        if data.get('error') == 'Username is already in use':
            # Username conflict. Add random suffix and retry
            return register(
                user, event, api_url, login_url, '.' + get_new_identifier(length=5)
            )
        logger.info('Bad Request during register: %s', data)
        # Probably already registered. Try logging in
        return login(user, event, 'login', login_url, api_url)
    else:
        logger.error(
            'Error while rocket chat registration: %d %s',
            res.status_code,
            data,
        )
        raise RocketChatException('Error while registration', response=res)


def check_or_create_bot(event: Event, api_url='', login_url=''):
    settings = get_settings()
    bot_email = settings['rocket_bot_email'] or 'openeventbot@openevent.com'
    bot_pass = settings['rocket_bot_pass'] or 'openeventbot'

    bot_user = User.query.filter_by(_email=bot_email).first_or_404()

    if not (bot_email):
        bot_user, _ = get_or_create(
            User, _email=bot_email, _password=bot_pass, first_name='openeventbot'
        )
        get_or_create(Setting, rocket_bot_email=bot_email, rocket_bot_pass=bot_pass)
        register(bot_user, event, api_url, login_url, '', True)

    return bot_user


def create_room(event: Event, user_id, api_url='', login_url=''):
    bot_info = check_or_create_bot(event, api_url, login_url)
    data = get_rocket_chat_token(bot_info, event, False, True)
    bot_token = data['token']
    bot_id = data['res']['data']['userId']

    res = requests.post(
        api_url + '/api/v1/groups.create',
        json=dict(name=event.name + event.identifier, members=[bot_id]),
        headers={
            'X-Auth-Token': bot_token,
            'X-User-Id': bot_id,
        },
    )
    if not res.status_code == 200:
        logger.error('Error while creating room : %s', res.json())
        raise RocketChatException('Error while creating room', response=res)
    else:
        group_data = res.json()
        event.chat_room_id = group_data['group']['_id']
        db.session.add(event)
        db.session.commit()
        add_in_room(event, user_id, api_url, login_url)


def add_in_room(event: Event, rocket_user_id, api_url='', login_url=''):
    bot_info = check_or_create_bot(event, api_url, login_url)
    data = get_rocket_chat_token(bot_info, event, False, True)
    bot_token = data['token']
    bot_id = data['res']['data']['userId']
    room_info = {'roomId': event.chat_room_id, 'userId': rocket_user_id}

    res = requests.post(
        api_url + '/api/v1/groups.invite',
        json=room_info,
        headers={
            'X-Auth-Token': bot_token,
            'X-User-Id': bot_id,
        },
    )

    if not res.status_code == 200:
        logger.error('Error while adding user : %s', res.json())
        raise RocketChatException('Error while adding user', response=res)


def get_rocket_chat_token(
    user: User, event: Event, retried: bool = False, is_bot: bool = False
):
    settings = get_settings()
    if not (api_url := settings['rocket_chat_url']):
        raise RocketChatException(
            'Rocket Chat Integration is not enabled', RocketChatException.CODES.DISABLED
        )

    login_url = api_url + '/api/v1/login'

    if user.rocket_chat_token:
        res = requests.post(login_url, json=dict(resume=user.rocket_chat_token))

        data = res.json()
        if res.status_code == 200:
            if not is_bot:
                if not event.chat_room_id:
                    create_room(event, data['data']['userId'], api_url, login_url)
                else:
                    add_in_room(event, data['data']['userId'], api_url, login_url)
            return dict(method='resumed', token=user.rocket_chat_token, res=data)
        elif res.status_code == 401:
            # Token Expired. Login again

            try:
                return login(user, event, 'login', login_url, api_url)
            except RocketChatException as rce:
                if (
                    not retried
                    and rce.response is not None
                    and rce.response.status_code == 401
                ):
                    # Invalid credentials stored. Reset credentials and retry
                    # If we have already retried, give up
                    user.rocket_chat_token = None
                    db.session.add(user)
                    db.session.commit()
                    if is_bot:
                        return get_rocket_chat_token(
                            user, event, retried=True, is_bot=True
                        )
                    else:
                        return get_rocket_chat_token(user, event, retried=True)
                else:
                    raise rce
        else:
            # Unhandled Case
            logger.error('Error while rocket chat resume or login: %s', data)
            raise RocketChatException('Error while resume or logging in', response=res)
    else:
        # No token. Try creating profile, else login

        return register(user, event, api_url, login_url, '')
