from freshbooks.errors import FreshBooksError
from freshbooks.api.resource import HttpVerbs, Resource
from freshbooks.models import Identity
from decimal import Decimal


class AuthResource(Resource):

    def _get_url(self, endpoint):
        return "{}/auth/api/v1/{}".format(self.base_url, endpoint)

    def _request(self, url, method, data=None):
        response = self._send_request(url, method, data)

        status = response.status_code
        try:
            content = response.json(parse_float=Decimal)
        except ValueError:
            raise FreshBooksError(status, "Failed to parse response", raw_response=response.text)

        if status >= 400:
            error = content.get("error", "Unknown Error")
            message = content.get("error_description")
            raise FreshBooksError(status, message, error_code=error, raw_response=content)

        if "response" not in content:
            raise FreshBooksError(status, "Returned an unexpected response", raw_response=response.text)
        return content["response"]

    def me_endpoint(self):
        data = self._request(self._get_url("users/me"), HttpVerbs.GET)
        return Identity(data)
