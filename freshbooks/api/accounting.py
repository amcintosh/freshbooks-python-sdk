from decimal import Decimal
from types import SimpleNamespace
from typing import Any, List, Optional, Tuple, Union

from freshbooks.api.resource import HttpVerbs, Resource
from freshbooks.builders import Builder
from freshbooks.builders.includes import IncludesBuilder
from freshbooks.errors import FreshBooksError, FreshBooksNotImplementedError
from freshbooks.models import ListResult, Result, VisState


class AccountingResource(Resource):
    """Handles resources under the `/accounting` endpoints."""

    def __init__(self, client_config: SimpleNamespace, accounting_path: str,
                 single_name: str, list_name: str,
                 delete_via_update: bool = True, missing_endpoints: Optional[List[str]] = None):
        super().__init__(client_config)
        self.accounting_path = accounting_path
        self.single_name = single_name
        self.list_name = list_name
        self.delete_via_update = delete_via_update
        self.missing_endpoints = missing_endpoints or []

    def _get_url(self, account_id: str, resource_id: Optional[int] = None) -> str:
        if resource_id:
            return "{}/accounting/account/{}/{}/{}".format(
                self.base_url, account_id, self.accounting_path, resource_id)
        return "{}/accounting/account/{}/{}".format(self.base_url, account_id, self.accounting_path)

    def _extract_error(self, errors: Union[list, dict]) -> Tuple[str, Optional[int]]:
        if not errors:  # pragma: no cover
            return "Unknown error", None

        if isinstance(errors, list):
            return errors[0]["message"], int(errors[0]["errno"])

        return errors["message"], int(errors["errno"])  # pragma: no cover

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

        if "response" not in content:
            raise FreshBooksError(status, "Returned an unexpected response", raw_response=response.text)

        response_data = content["response"]
        if status >= 400:
            message, code = self._extract_error(response_data["errors"])
            raise FreshBooksError(status, message, error_code=code, raw_response=content)
        try:
            return response_data["result"]
        except KeyError:
            return response_data

    def _reject_missing(self, name: str) -> None:
        if name in self.missing_endpoints:
            raise FreshBooksNotImplementedError(self.list_name, name)

    def get(self, account_id: str, resource_id: int, includes: Optional[IncludesBuilder] = None) -> Result:
        """Get a single resource with the corresponding id.

        Args:
            account_id: The alpha-numeric account id
            resource_id: Id of the resource to return
            builders: (Optional) IncludesBuilder object for including additional data, sub-resources, etc.
        Returns:
            Result: Result object with the resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("get")
        resource_url = self._get_url(account_id, resource_id)
        query_string = ""
        if includes:
            query_string = self._build_query_string([includes])
        data = self._request(f"{resource_url}{query_string}", HttpVerbs.GET)
        return Result(self.single_name, data)

    def list(self, account_id: str, builders: Optional[List[Builder]] = None) -> ListResult:
        """Get a list of resources.

        Args:
            account_id: The alpha-numeric account id
            builders: (Optional) List of builder objects for filters, pagination, etc.

        Returns:
            ListResult: ListResult object with the resources response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("list")
        resource_url = self._get_url(account_id)
        query_string = self._build_query_string(builders)
        data = self._request(f"{resource_url}{query_string}", HttpVerbs.GET)
        return ListResult(self.list_name, self.single_name, data)

    def create(self, account_id: str, data: dict, includes: Optional[IncludesBuilder] = None) -> Result:
        """Create a resource.

        Args:
            account_id: The alpha-numeric account id
            data: Dictionary of data to populate the resource
            builders: (Optional) IncludesBuilder object for including additional data, sub-resources, etc.

        Returns:
            Result: Result object with the new resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("create")
        resource_url = self._get_url(account_id)
        query_string = ""
        if includes:
            query_string = self._build_query_string([includes])
        response = self._request(f"{resource_url}{query_string}", HttpVerbs.POST, data={self.single_name: data})
        return Result(self.single_name, response)

    def update(
        self, account_id: str, resource_id: int, data: dict, includes: Optional[IncludesBuilder] = None
    ) -> Result:
        """Update a resource.

        Args:
            account_id: The alpha-numeric account id
            resource_id: Id of the resource to update
            data: Dictionary of data to update the resource to
            builders: (Optional) IncludesBuilder object for including additional data, sub-resources, etc.

        Returns:
            Result: Result object with the updated resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("update")
        resource_url = self._get_url(account_id, resource_id)
        query_string = ""
        if includes:
            query_string = self._build_query_string([includes])
        response = self._request(f"{resource_url}{query_string}", HttpVerbs.PUT, data={self.single_name: data})
        return Result(self.single_name, response)

    def delete(self, account_id: str, resource_id: int) -> Result:
        """Delete a resource.

        Note: Most FreshBooks resources are soft-deleted,
        See [FreshBooks API - Active and Deleted Objects](https://www.freshbooks.com/api/active_deleted)

        Args:
            account_id: The alpha-numeric account id
            resource_id: Id of the resource to delete

        Returns:
            Result: An empty Result object.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("delete")
        if self.delete_via_update:
            response = self._request(
                self._get_url(account_id, resource_id),
                HttpVerbs.PUT,
                data={self.single_name: {"vis_state": VisState.DELETED}}
            )
        else:
            response = self._request(self._get_url(account_id, resource_id), HttpVerbs.DELETE)
        return Result(self.single_name, response)
