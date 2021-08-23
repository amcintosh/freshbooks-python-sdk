from types import SimpleNamespace
from typing import List, Optional

from freshbooks.api.projects import ProjectsResource, ProjectsBaseResource
from freshbooks.api.resource import HttpVerbs
from freshbooks.builders import Builder
from freshbooks.models import ListResult, Result


class CommentsResource(ProjectsResource):
    """Handles resources under the `/comments` endpoints.

    These are handled identically to `/projects` endpoints.
    Refer to `freshbooks.api.projects.ProjectsResource`.
    """

    def _get_url(self, business_id: int, resource_id: Optional[int] = None, is_list: Optional[bool] = False) -> str:
        if resource_id:
            return "{}/comments/business/{}/{}/{}".format(
                self.base_url, business_id, self.single_resource_path, resource_id)
        if is_list:
            return "{}/comments/business/{}/{}".format(self.base_url, business_id, self.list_resource_path)
        return "{}/comments/business/{}/{}".format(self.base_url, business_id, self.single_resource_path)


class CommentsSubResource(ProjectsBaseResource):
    """Handles sub-resources under the `/comments` endpoints.

    Eg. `/comments/business/{business_id}/services/{service_id}/rate`

    These are handled similarly to `/projects` endpoints.
    Refer to `freshbooks.api.projects.ProjectsResource`.
    """
    def __init__(self, client_config: SimpleNamespace,
                 list_resource_path: str, single_resource_path: str,
                 single_resource_sub_path: Optional[str] = None,
                 list_name: Optional[str] = None, single_name: Optional[str] = None,
                 missing_endpoints: Optional[List[str]] = None):

        super().__init__(
            client_config, list_resource_path, single_resource_path, list_name, single_name, missing_endpoints
        )
        self.single_resource_sub_path = single_resource_sub_path

    def _get_url(self, business_id: int, resource_id: Optional[int] = None, is_list: Optional[bool] = False) -> str:
        if resource_id:
            return "{}/comments/business/{}/{}/{}/{}".format(
                self.base_url, business_id, self.single_resource_path, resource_id, self.single_resource_sub_path)
        if is_list:  # pragma: no branch
            return "{}/comments/business/{}/{}".format(self.base_url, business_id, self.list_resource_path)
        return "{}/comments/business/{}/{}".format(
            self.base_url, business_id, self.single_resource_path)  # pragma: no cover

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

    def create(self, business_id: int, resource_id: int, data: dict) -> Result:
        """Create a resource.

        Args:
            business_id: The business id
            resource_id: Id of the parent resource to create this resource under
            data: Dictionary of data to populate the resource

        Returns:
            Result: Result object with the new resource's response data.

        Raises:
            FreshBooksError: If the call is not successful.
        """
        self._reject_missing("create")
        response = self._request(
            self._get_url(business_id, resource_id), HttpVerbs.POST, data={self.single_name: data}
        )
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

    def delete(self, business_id: int, resource_id: int) -> Result:  # pragma: no cover
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
