import json
from enum import Enum
from typing import List
from typing import Dict
import base64

from .user import User
from .webhook import Webhook
from .movie import Movie

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


BASE_API_URI = "https://apiv2.twitcasting.tv/"


class Auth(Enum):
    BASIC = 'Basic '
    OAUTH = 'Bearer '
    NONE = ''


class API:
    def __init__(self, client_id: str, client_secret: str, access_token: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token
        self._session = requests.Session()

    def _generate_auth(self, auth: Auth):
        if auth is Auth.BASIC:
            return {'Authorization': Auth.BASIC.value + base64.b64encode(f'{self._client_id}:{self._client_secret}'.encode("utf-8")).decode("utf-8")}
        elif auth is Auth.OAUTH:
            return {'Authorization': Auth.OAUTH.value + self._access_token}
        else:
            return {}

    def _api_call(self, method: str, url: str, payload: object = None, json_data: Dict[str, str] = None, auth: Auth = None, params: dict = None):
        _url = BASE_API_URI + url

        args = dict(params=params)
        if payload:
            args['data'] = json.dumps(payload)
        if json:
            args['json'] = json_data

        _headers = self._generate_auth(auth)
        _headers['X-Api-Version'] = '2.0'
        _headers['Accept'] = 'application/json'

        r = self._session.request(method, _url, headers=_headers, **args)

        # TODO: HTTP error handling

        if r.text and r.text != 'null':
            if r.headers['Content-Type'] in ['image/jpeg', 'image/png']:
                file_ext = r.headers['Content-Type'].replace('image/', '')
                ret = {'bytes_data': r.content,
                       'file_ext': file_ext}
                return ret
            else:
                return r.json()
        else:
            return None

    def _get(self, url: str, args: dict = None, payload: object = None, json_data: Dict[str, str] = None, auth: Auth = None, **kwargs):
        if args:
            kwargs.update(args)

        return self._api_call('GET', url, payload, json_data, auth, kwargs)

    def _post(self, url: str, args: dict = None, payload: object = None, json_data: Dict[str, str] = None, auth: Auth = None, **kwargs):
        if args:
            kwargs.update(args)

        return self._api_call('POST', url, payload, json_data, auth, kwargs)

    def _delete(self, url: str, args: dict = None, payload: object = None, json_data: Dict[str, str] = None, auth: Auth = None, **kwargs):
        if args:
            kwargs.update(args)

        return self._api_call('DELETE', url, payload, json_data, auth, kwargs)

    def search_users(self, words: List[str], limit: int = 10, lang: str = 'ja'):
        if isinstance(words, list):
            w = ' '.join(words) if len(words) > 1 else words[0]
        else:
            w = words
        res = self._get(url='/search/users', auth=Auth.OAUTH, words=w, limit=limit, lang=lang)
        return User.parse_list(self, res['users'])

    def get_webhook_list(self, limit: int = 50, offset: int = 0, user_id: str = None):
        res = self._get(url='/webhooks', auth=Auth.BASIC, limit=limit, offset=offset, user_id=user_id)
        return Webhook.parse_list(self, res['webhooks'])

    def register_webhook(self, user_id: str = None, events: List[str] = ['livestart', 'liveend']):
        data = {'user_id': user_id, 'events': events}
        return self._post(url='/webhooks', auth=Auth.BASIC, json_data=data)

    def remove_webhook(self, user_id: str = None, events: List[str] = ['livestart', 'liveend']):
        params = {'user_id': user_id, 'events[]': events}
        return self._delete(url='/webhooks', auth=Auth.BASIC, args=params)

    def parse_incoming_webhook(self, res):
        movie = Movie.parse(self, res['movie'])
        user = User.parse(self, res['broadcaster'])
        return movie, user
