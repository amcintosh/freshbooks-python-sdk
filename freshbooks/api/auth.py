from decimal import Decimal
from typing import Any, Optional

from freshbooks.api.resource import HttpVerbs, Resource
from freshbooks.errors import FreshBooksError
from freshbooks.models import Identity


class AuthResource(Resource):
    """Handles resources under the `/auth` endpoints."""

    def _get_url(self, endpoint: str) -> str:
        return "{}/auth/api/v1/{}".format(self.base_url, endpoint)

    def _request(self, url: str, method: str, data: Optional[dict] = None) -> Any:
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

    def me_endpoint(self) -> Identity:
        """Get the identity details of the currently authenticated user.

        See [FreshBooks API - Business, Roles, and Identity](https://www.freshbooks.com/api/me_endpoint)

        Returns:
            Result: Result object with the authenticated user's identity and business details.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        data = self._request(self._get_url("users/me"), HttpVerbs.GET)
        return Identity(data)
