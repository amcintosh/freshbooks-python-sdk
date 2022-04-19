from decimal import Decimal
from types import SimpleNamespace
from typing import Any, List, Optional

from freshbooks.api.resource import HttpVerbs, Resource
from freshbooks.errors import FreshBooksError, FreshBooksNotImplementedError
from freshbooks.models import Result


class PaymentsResource(Resource):
    """Handles resources under the `/payments` endpoints."""

    def __init__(self, client_config: SimpleNamespace, path: str, single_name: str,
                 sub_path: Optional[str] = None,
                 defaults_path: Optional[str] = None,
                 static_params: Optional[str] = None,
                 missing_endpoints: Optional[List[str]] = None):
        super().__init__(client_config)
        self.path = path
        self.single_name = single_name
        self.sub_path = sub_path
        self.defaults_path = defaults_path
        self.static_params = static_params
        self.missing_endpoints = missing_endpoints or []

    def _get_url(self, account_id: str, resource_id: Optional[int] = None) -> str:
        if resource_id and self.sub_path:
            url = f"{self.base_url}/payments/account/{account_id}/{self.path}/{resource_id}/{self.sub_path}"
        else:
            url = f"{self.base_url}/payments/account/{account_id}/{self.defaults_path}"
            if self.static_params:  # pragma: no branch
                url += f"?{self.static_params}"
        return url

    def _extract_error(self, errors: dict) -> str:
        if not errors.get("errors") and not errors.get("message"):  # pragma: no cover
            return "Unknown error"
        if errors.get("errors"):
            error_details = errors.get("errors")
            if isinstance(error_details, list):
                return f"{error_details[0]['field']}: {error_details[0]['message']}"
            else:  # pragma: no cover
                return f"{error_details['field']}: {error_details['message']}"  # type: ignore
        return errors["message"]  # type: ignore

    def _request(self, url: str, method: str, data: Optional[dict] = None) -> Any:
        response = self._send_request(url, method, data)

        status = response.status_code
        if status == 200 and method == HttpVerbs.HEAD:  # pragma: no cover
            # no content returned from a HEAD
            return

        try:
            content = response.json(parse_float=Decimal)
        except ValueError:
            raise FreshBooksError(status, "Failed to parse response", raw_response=response.text)

        if status >= 400:
            message = self._extract_error(content)
            raise FreshBooksError(status, message, raw_response=content)
        return content

    def _reject_missing(self, name: str) -> None:
        if name in self.missing_endpoints:  # pragma: no cover
            raise FreshBooksNotImplementedError(self.single_name, name)

    def defaults(self, account_id: str) -> Result:
        """Get the default settings for an account resource.

        Args:
            account_id: The alpha-numeric account id
        Returns:
            Result: Result object with the default data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("defaults")
        resource_url = self._get_url(account_id)
        data = self._request(resource_url, HttpVerbs.GET)
        return Result(self.single_name, data)

    def get(self, account_id: str, resource_id: int) -> Result:
        """Get a single resource with the corresponding id.

        Args:
            account_id: The alpha-numeric account id
            resource_id: Id of the resource to return payment details for
        Returns:
            Result: Result object with the resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("get")
        resource_url = self._get_url(account_id, resource_id)
        data = self._request(resource_url, HttpVerbs.GET)
        return Result(self.single_name, data)

    def create(self, account_id: str, resource_id: int, data: dict) -> Result:
        """Create a resource.

        Args:
            account_id: The alpha-numeric account id
            resource_id: Id of the resource to create payment details for
            data: Dictionary of data to populate the resource

        Returns:
            Result: Result object with the new resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("create")
        resource_url = self._get_url(account_id, resource_id)
        response = self._request(resource_url, HttpVerbs.POST, data=data)
        return Result(self.single_name, response)
