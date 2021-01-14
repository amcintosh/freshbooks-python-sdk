import json
from types import SimpleNamespace
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class HttpVerbs(object):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"


class Resource:
    API_RETRIES = 3
    """Default number of retries"""

    def __init__(self, client_config: SimpleNamespace):
        self.base_url = client_config.base_url
        self.access_token = client_config.access_token
        self.user_agent = client_config.user_agent
        self.timeout = client_config.timeout
        self.session = self._config_session(client_config.auto_retry)

    def _config_session(self, auto_retry: bool) -> requests.Session:
        session = requests.Session()

        if auto_retry:
            retry = Retry(  # type: ignore
                total=self.API_RETRIES,
                backoff_factor=0.3,
                allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
                status_forcelist=[400, 408, 429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

        return session

    def headers(self, method: str) -> Dict[str, str]:
        """Get headers required for API calls"""

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "user-agent": self.user_agent
        }
        if method in [HttpVerbs.POST, HttpVerbs.PUT, HttpVerbs.PATCH]:
            headers["Content-Type"] = "application/json"
        return headers

    def _send_request(self, uri: str, method: str, data: Optional[dict] = None) -> Any:
        payload = None
        if method is HttpVerbs.GET:
            session = self.session.get
        elif method is HttpVerbs.POST:
            session = self.session.post
            payload = json.dumps(data)
        elif method is HttpVerbs.PUT:
            session = self.session.put
            payload = json.dumps(data)
        elif method is HttpVerbs.PATCH:  # pragma: no cover
            session = self.session.patch
            payload = json.dumps(data)
        elif method is HttpVerbs.DELETE:
            session = self.session.delete
        elif method is HttpVerbs.HEAD:  # pragma: no cover
            session = self.session.head

        try:
            res = session(uri, data=payload, headers=self.headers(method), timeout=self.timeout)
        except requests.exceptions.RetryError:
            adapter = HTTPAdapter()
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
            res = session(uri, data=payload, headers=self.headers(method), timeout=self.timeout)

        return res

    def _build_query_string(self, builders: Any) -> str:
        query_string = ""
        if builders:
            for builder in builders:
                query_string += builder.build(self.__class__.__name__)
        if query_string:
            query_string = "?" + query_string[1:]
        return query_string
