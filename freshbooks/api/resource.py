import json
import requests


class HttpVerbs(object):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"


class Resource:
    DEFAULT_TIMEOUT = 30
    """Default request timeout to FreshBooks"""

    def __init__(self, client_config):
        self.base_url = client_config.base_url
        self.access_token = client_config.access_token
        self.user_agent = client_config.user_agent
        self.session = requests.Session()

    def headers(self, method):
        """Get headers required for API calls"""

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "user-agent": self.user_agent
        }
        if method in [HttpVerbs.POST, HttpVerbs.PUT, HttpVerbs.PATCH]:
            headers["Content-Type"] = "application/json"
        return headers

    def _send_request(self, uri, method, data):
        if method is HttpVerbs.GET:
            session = self.session.get
        elif method is HttpVerbs.POST:
            session = self.session.post
            data = json.dumps(data)
        elif method is HttpVerbs.PUT:
            session = self.session.put
            data = json.dumps(data)
        elif method is HttpVerbs.PATCH:
            session = self.session.patch
            data = json.dumps(data)
        elif method is HttpVerbs.DELETE:
            session = self.session.delete
        elif method is HttpVerbs.HEAD:
            session = self.session.head

        return session(uri, data=data, headers=self.headers(method), timeout=self.DEFAULT_TIMEOUT)

    def _build_query_string(self, builders):
        query_string = ""
        if builders:
            for builder in builders:
                query_string += builder.build()
        if query_string:
            query_string = "?" + query_string[1:]
        return query_string
