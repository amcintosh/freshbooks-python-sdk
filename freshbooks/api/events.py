from typing import Tuple
from decimal import Decimal
from typing import Any, Optional

from freshbooks.api.accounting import AccountingResource
from freshbooks.api.resource import HttpVerbs
from freshbooks.errors import FreshBooksError
from freshbooks.models import Result


class EventsResource(AccountingResource):
    """Handles resources under the `/events` endpoints.

    These are handled almost similarly to `/accounting` endpoints.
    Refer to `freshbooks.api.accounting.AccountingResource`.
    """

    def _get_url(self, account_id: str, resource_id: Optional[int] = None) -> str:
        if resource_id:
            return "{}/events/account/{}/{}/{}".format(
                self.base_url, account_id, self.accounting_path, resource_id)
        return "{}/events/account/{}/{}".format(self.base_url, account_id, self.accounting_path)

    def _extract_error_details(self, errors: dict) -> Tuple[str, Optional[int], Optional[dict]]:
        if not errors:  # pragma: no cover
            return "Unknown error", None, None

        details = None
        for detail in errors.get("details", []):
            if detail.get("@type") == "type.googleapis.com/google.rpc.BadRequest":
                details = detail

        return errors["message"], int(errors["code"]), details

    def _request(self, url: str, method: str, data: Optional[dict] = None) -> Any:
        response = self._send_request(url, method, data)

        status = response.status_code
        if status == 200 and method == HttpVerbs.HEAD:  # pragma: no cover
            # no content returned from a HEAD
            return
        if status == 204 and method == HttpVerbs.DELETE:
            return {}

        try:
            content = response.json(parse_float=Decimal)
        except ValueError:
            raise FreshBooksError(status, "Failed to parse response", raw_response=response.text)

        if status >= 400:
            error_message, error_code, error_details = self._extract_error_details(content)
            raise FreshBooksError(
                status, error_message, error_code=error_code, error_details=error_details, raw_response=content
            )

        if "response" not in content:
            raise FreshBooksError(status, "Returned an unexpected response", raw_response=response.text)

        return content["response"]["result"]

    def verify(self, account_id: str, resource_id: int, verifier: str) -> Result:
        """Verify webhook callback by making a put request

        Args:
            account_id: The alpha-numeric account id
            resource_id: Id of the resource to update
            verifier: The string verifier received by the webhook callback URI

        Returns:
            Result: Result object with the resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        response = self._request(
            self._get_url(account_id, resource_id), HttpVerbs.PUT, data={self.single_name: {"verifier": verifier}}
        )
        return Result(self.single_name, response)

    def resend_verification(self, account_id: str, resource_id: int) -> Result:
        """Tell FreshBooks to resend the verification webhook for the callback

        Args:
            account_id: The alpha-numeric account id
            resource_id: Id of the resource to update

        Returns:
            Result: Result object with the resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        response = self._request(
            self._get_url(account_id, resource_id), HttpVerbs.PUT, data={self.single_name: {"resend": True}}
        )
        return Result(self.single_name, response)
