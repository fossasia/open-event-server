from dataclasses import dataclass
from hashlib import sha1
from typing import Any, Dict, Union, Optional

import requests
import xmltodict
from urllib3.request import urlencode


@dataclass
class Result:
    success: bool
    response: Any
    data: Union[None, Dict[str, Any]]

    @staticmethod
    def create(response: Any) -> 'Result':
        success = response.status_code == 200

        data = None
        if success:
            data = xmltodict.parse(response.content, dict_constructor=dict)
            success = data.get('response', {}).get('returncode') == 'SUCCESS'
        return Result(success=success, response=response, data=data)


@dataclass
class BigBlueButton:
    api_url: str
    secret: str

    def build_url(self, action: str, params: Optional[Dict[str, str]] = None) -> str:
        url = self.api_url + '/' + action + '?'

        params = params or {}
        params = {key: val for (key, val) in params.items() if val}
        query = urlencode(params)

        url += query + '&checksum=' + self._checksum(action, query)

        return url

    def _checksum(self, action: str, query: str):
        key = action + query + self.secret
        return sha1(key.encode('utf-8')).hexdigest()

    def request(self, action: str, params: Optional[Dict[str, str]] = None) -> Result:
        return Result.create(requests.get(self.build_url(action, params)))
