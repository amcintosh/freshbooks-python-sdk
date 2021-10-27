from decimal import Decimal
from types import SimpleNamespace
from typing import Any, List, Optional

from freshbooks.api.resource import HttpVerbs, Resource
from freshbooks.builders import Builder
from freshbooks.errors import FreshBooksError, FreshBooksNotImplementedError
from freshbooks.models import ListResult, Result


class ProjectsBaseResource(Resource):
    """Shared project-like response handling"""

    def __init__(self, client_config: SimpleNamespace,
                 list_resource_path: str, single_resource_path: str,
                 list_name: Optional[str] = None, single_name: Optional[str] = None,
                 missing_endpoints: Optional[List[str]] = None):

        super().__init__(client_config)
        self.list_resource_path = list_resource_path
        self.list_name = list_name
        if not list_name:  # pragma: no branch
            self.list_name = list_resource_path

        self.single_resource_path = single_resource_path
        self.single_name = single_name
        if not single_name:  # pragma: no branch
            self.single_name = single_resource_path

        self.missing_endpoints = missing_endpoints or []

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
            code = content.get("errno")
            message = content.get("message") or content.get("error", "Unknown error")
            raise FreshBooksError(status, message, error_code=code, raw_response=content)
        return content

    def _reject_missing(self, name: str) -> None:
        if name in self.missing_endpoints:
            raise FreshBooksNotImplementedError(self.list_name or self.list_resource_path, name)


class ProjectsResource(ProjectsBaseResource):
    """Handles resources under the `/projects` endpoints."""

    def _get_url(self, business_id: int, resource_id: Optional[int] = None, is_list: Optional[bool] = False) -> str:
        if resource_id:
            return "{}/projects/business/{}/{}/{}".format(
                self.base_url, business_id, self.single_resource_path, resource_id)
        if is_list:
            return "{}/projects/business/{}/{}".format(self.base_url, business_id, self.list_resource_path)
        return "{}/projects/business/{}/{}".format(self.base_url, business_id, self.single_resource_path)

    def get(self, business_id: int, resource_id: int) -> Result:
        """Get a single resource with the corresponding id.

        Args:
            business_id: The business id
            resource_id: Id of the resource to return
        Returns:
            Result: Result object with the resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("get")
        data = self._request(self._get_url(business_id, resource_id), HttpVerbs.GET)
        return Result(self.single_name, data)

    def list(self, business_id: int, builders: Optional[List[Builder]] = None) -> ListResult:
        """Get a list of resources.

        Args:
            business_id: The business id
            builders: (Optional) List of builder objects for filters, pagination, etc.

        Returns:
            ListResult: ListResult object with the resources response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("list")
        resource_url = self._get_url(business_id, is_list=True)
        query_string = self._build_query_string(builders)
        data = self._request(f"{resource_url}{query_string}", HttpVerbs.GET)
        return ListResult(self.list_name, self.single_name, data)  # type: ignore

    def create(self, business_id: int, data: dict) -> Result:
        """Create a resource.

        Args:
            business_id: The business id
            data: Dictionary of data to populate the resource

        Returns:
            Result: Result object with the new resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("create")
        response = self._request(self._get_url(business_id), HttpVerbs.POST, data={self.single_name: data})
        return Result(self.single_name, response)

    def update(self, business_id: int, resource_id: int, data: dict) -> Result:
        """Update a resource.

        Args:
            business_id: The business id
            resource_id: Id of the resource to update
            data: Dictionary of data to update the resource to

        Returns:
            Result: Result object with the updated resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("update")
        response = self._request(
            self._get_url(business_id, resource_id), HttpVerbs.PUT, data={self.single_name: data}
        )
        return Result(self.single_name, response)

    def delete(self, business_id: int, resource_id: int) -> Result:
        """Delete a resource.

        Note: Most FreshBooks resources are soft-deleted,
        See [FreshBooks API - Active and Deleted Objects](https://www.freshbooks.com/api/active_deleted)

        Args:
            business_id: The business id
            resource_id: Id of the resource to delete

        Returns:
            Result: An empty Result object.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("delete")
        response = self._request(self._get_url(business_id, resource_id), HttpVerbs.DELETE)
        return Result(self.single_name, response)
