from decimal import Decimal
from types import SimpleNamespace
from typing import Any, List, Optional, Tuple

from freshbooks.api.resource import HttpVerbs, Resource
from freshbooks.errors import FreshBooksError, FreshBooksNotImplementedError
from freshbooks.models import ListResult, Result


class AccountingBusinessResource(Resource):
    """Handles resources under the `/accounting/businesses/` endpoints."""

    def __init__(self, client_config: SimpleNamespace, path: str, resource_name: str,
                 missing_endpoints: Optional[List[str]] = None):
        super().__init__(client_config)
        self.path = path
        self.resource_name = resource_name
        self.missing_endpoints = missing_endpoints or []

    def _get_url(self, business_uuid: str, resource_uuid: Optional[str] = None) -> str:
        if resource_uuid:
            return "{}/accounting/businesses/{}/{}/{}".format(
                self.base_url, business_uuid, self.path, resource_uuid)
        return "{}/accounting/businesses/{}/{}".format(self.base_url, business_uuid, self.path)

    def _extract_error(self, response_data: dict) -> Tuple[str, Optional[List[dict]]]:
        if not response_data.get("errors", {}).get("message"):  # pragma: no cover
            return "Unknown error", None
        errors = response_data["errors"]
        message = errors["message"]
        details = []
        for detail in errors.get("details", []):
            if detail.get("reason"):  # pragma: no branch
                message = detail["reason"]
            if detail.get("metadata"):  # pragma: no branch
                details.append(detail["metadata"])
        return message, details

    def _request(self, url: str, method: str, data: Optional[dict] = None) -> Any:
        response = self._send_request(url, method, data)

        status = response.status_code
        if status == 200 and method == HttpVerbs.HEAD:  # pragma: no cover
            # no content returned from a HEAD
            return
        if status == 204 and method == HttpVerbs.DELETE:
            return {"data": {}}

        try:
            response_data = response.json(parse_float=Decimal)
        except ValueError:
            raise FreshBooksError(status, "Failed to parse response", raw_response=response.text)

        if status >= 400:
            message, error_details = self._extract_error(response_data)
            raise FreshBooksError(
                status, message, error_details=error_details, raw_response=response_data
            )
        if "data" not in response_data.keys():
            raise FreshBooksError(status, "Returned an unexpected response", raw_response=response.text)
        return response_data

    def _reject_missing(self, name: str) -> None:
        if name in self.missing_endpoints:
            raise FreshBooksNotImplementedError(self.resource_name, name)

    def get(self, business_uuid: str, resource_uuid: str) -> Result:
        """Get a single resource with the corresponding id.

        Args:
            business_uuid: The business uuid
            resource_uuid: Id of the resource to return
        Returns:
            Result: Result object with the resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("get")
        resource_url = self._get_url(business_uuid, resource_uuid)
        data = self._request(resource_url, HttpVerbs.GET)
        return Result(self.resource_name, {self.resource_name: data["data"]})

    def list(self, business_uuid: str) -> ListResult:
        """Get a list of resources.

        Args:
            business_uuid: The business uuid

        Returns:
            ListResult: ListResult object with the resources response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("list")
        resource_url = self._get_url(business_uuid)
        data = self._request(resource_url, HttpVerbs.GET)
        return ListResult(self.resource_name, self.resource_name, {self.resource_name: data["data"]})

    def create(self, business_uuid: str, data: dict) -> Result:
        """Create a resource.

        Args:
            business_uuid: The business uuid
            data: Dictionary of data to populate the resource

        Returns:
            Result: Result object with the new resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("create")
        resource_url = self._get_url(business_uuid)
        response = self._request(resource_url, HttpVerbs.POST, data=data)
        return Result(self.resource_name, {self.resource_name: response["data"]})

    def update(
        self, business_uuid: str, resource_uuid: str, data: dict
    ) -> Result:
        """Update a resource.

        Args:
            business_uuid: The business uuid
            resource_uuid: Id of the resource to return
            data: Dictionary of data to update the resource to

        Returns:
            Result: Result object with the updated resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("update")
        resource_url = self._get_url(business_uuid, resource_uuid)
        response = self._request(resource_url, HttpVerbs.PUT, data=data)
        return Result(self.resource_name, {self.resource_name: response["data"]})

    def delete(self, business_uuid: str, resource_uuid: str) -> Result:
        """Delete a resource.

        Note: Most FreshBooks resources are soft-deleted,
        See [FreshBooks API - Active and Deleted Objects](https://www.freshbooks.com/api/active_deleted)

        Args:
            business_uuid: The business uuid
            resource_uuid: Id of the resource to return

        Returns:
            Result: An empty Result object.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("delete")
        response = self._request(self._get_url(business_uuid, resource_uuid), HttpVerbs.DELETE)
        return Result(self.resource_name, {self.resource_name: response["data"]})
