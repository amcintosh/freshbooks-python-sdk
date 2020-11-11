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

    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.access_token = access_token
        self.session = requests.Session()

    def headers(self, method):
        """Get headers required for API calls"""

        headers = {"Authorization": f"Bearer {self.access_token}"}
        if method in [HttpVerbs.POST, HttpVerbs.PUT, HttpVerbs.PATCH]:
            headers["Content-Type"] = "application/json"
        return headers

    def _send_request(self, uri, method, data):
        if method is HttpVerbs.GET:
            session = self.session.get
        elif method is HttpVerbs.POST:
            session = self.session.post
        elif method is HttpVerbs.PUT:
            session = self.session.put
        elif method is HttpVerbs.PATCH:
            session = self.session.patch
        elif method is HttpVerbs.DELETE:
            session = self.session.delete
        elif method is HttpVerbs.HEAD:
            session = self.session.head

        return session(uri, data=data, headers=self.headers(method), timeout=self.DEFAULT_TIMEOUT)
