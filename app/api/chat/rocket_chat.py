import logging

import requests

from app.api.helpers.db import get_new_identifier
from app.models import db
from app.models.event import Event
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


def get_rocket_chat_token(user: User, event: Event, retried: bool = False):
    settings = get_settings()
    if not (api_url := settings['rocket_chat_url']):
        raise RocketChatException(
            'Rocket Chat Integration is not enabled', RocketChatException.CODES.DISABLED
        )

    def save_token(token):
        user.rocket_chat_token = token
        db.session.add(user)
        db.session.commit()

    login_url = api_url + '/api/v1/login'

    def create_room(user_id):
        if (
            settings['rocket_bot_email']
            and settings['rocket_bot_password']
            and settings['rocket_bot_name']
        ):
            login_data = requests.post(
                login_url,
                json=dict(
                    email=settings['rocket_bot_email'],
                    password=settings['rocket_bot_password'],
                ),
            ).json()
            bot_token = login_data['data']['authToken']
            bot_id = login_data['data']['userId']
            res = requests.post(
                api_url + '/api/v1/groups.create',
                json=dict(name=event.name + event.identifier, members=[bot_id]),
                headers={
                    'X-Auth-Token': bot_token,
                    'X-User-Id': bot_id,
                },
            )
            data = res.json()
            event.chat_room_id = data['group']['_id']
            db.session.add(event)
            db.session.commit()
            add_in_room(user_id)
        else:
            raise RocketChatException('Rocket Chat Bot Info is not present')

    def add_in_room(rocket_user_id):
        room_info = {'roomId': event.chat_room_id, 'userId': rocket_user_id}
        login_data = requests.post(
            login_url,
            json=dict(
                email=settings['rocket_bot_email'],
                password=settings['rocket_bot_password'],
            ),
        ).json()
        bot_token = login_data['data']['authToken']
        bot_id = login_data['data']['userId']
        res = requests.post(
            api_url + '/api/v1/groups.invite',
            json=room_info,
            headers={
                'X-Auth-Token': bot_token,
                'X-User-Id': bot_id,
            },
        )
        data = res.json()

    def login(method='login'):
        res = requests.post(
            login_url, json=dict(email=user.email, password=user.rocket_chat_password)
        )
        data = res.json()
        if res.status_code == 200:
            token = data['data']['authToken']
            save_token(token)
            if event.chat_room_id:
                add_in_room(data['data']['userId'])
            else:
                create_room(data['data']['userId'])
            return dict(method=method, token=token, res=data)
        else:
            # Unhandled Case
            logger.error('Error while rocket chat login: %s', data)
            raise RocketChatException('Error while logging in', response=res)

    def register(username_suffix=''):
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
            return login('registered')
        elif res.status_code == 400:
            if data.get('error') == 'Username is already in use':
                # Username conflict. Add random suffix and retry
                return register('.' + get_new_identifier(length=5))
            logger.info('Bad Request during register: %s', data)
            # Probably already registered. Try logging in
            return login()
        else:
            logger.error(
                'Error while rocket chat registration: %d %s',
                res.status_code,
                data,
            )
            raise RocketChatException('Error while registration', response=res)

    if user.rocket_chat_token:
        res = requests.post(login_url, json=dict(resume=user.rocket_chat_token))

        data = res.json()
        if res.status_code == 200:
            if not event.chat_room_id:
                create_room(data['data']['userId'])
            else:
                add_in_room(data['data']['userId'])
            return dict(method='resumed', token=user.rocket_chat_token, res=data)
        elif res.status_code == 401:
            # Token Expired. Login again

            try:
                return login()
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

                    return get_rocket_chat_token(user, event, retried=True)
                else:
                    raise rce
        else:
            # Unhandled Case
            logger.error('Error while rocket chat resume or login: %s', data)
            raise RocketChatException('Error while resume or logging in', response=res)
    else:
        # No token. Try creating profile, else login

        return register()
