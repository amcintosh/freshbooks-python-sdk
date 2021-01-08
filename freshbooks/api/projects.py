from decimal import Decimal
from types import SimpleNamespace
from typing import Any, List, Optional

from freshbooks.api.resource import HttpVerbs, Resource
from freshbooks.builders import Builder
from freshbooks.errors import FreshBooksError
from freshbooks.models import ListResult, Result


class ProjectsResource(Resource):
    """Handles resources under the `/projects` endpoints."""

    def __init__(self, client_config: SimpleNamespace,
                 list_resource_path: str, single_resource_path: str,
                 list_name: Optional[str] = None, single_name: Optional[str] = None):

        super().__init__(client_config)
        self.list_resource_path = list_resource_path
        self.list_name = list_name
        if not list_name:  # pragma: no branch
            self.list_name = list_resource_path

        self.single_resource_path = single_resource_path
        self.single_name = single_name
        if not single_name:  # pragma: no branch
            self.single_name = single_resource_path

    def _get_url(self, business_id: int, resource_id: Optional[int] = None, is_list: Optional[bool] = False) -> str:
        if resource_id:
            return "{}/projects/business/{}/{}/{}".format(
                self.base_url, business_id, self.single_resource_path, resource_id)
        if is_list:
            return "{}/projects/business/{}/{}".format(self.base_url, business_id, self.list_resource_path)
        return "{}/projects/business/{}/{}".format(self.base_url, business_id, self.single_resource_path)

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

    def get(self, business_id: int, resource_id: int) -> Result:
        data = self._request(self._get_url(business_id, resource_id), HttpVerbs.GET)
        return Result(self.single_name, data)

    def list(self, business_id: int, builders: Optional[List[Builder]] = None) -> ListResult:
        resource_url = self._get_url(business_id, is_list=True)
        query_string = self._build_query_string(builders)
        data = self._request(f"{resource_url}{query_string}", HttpVerbs.GET)
        return ListResult(self.list_name, self.single_name, data)  # type: ignore

    def create(self, business_id: int, data: dict) -> Result:
        response = self._request(self._get_url(business_id), HttpVerbs.POST, data={self.single_name: data})
        return Result(self.single_name, response)

    def update(self, business_id: int, resource_id: int, data: dict) -> Result:
        response = self._request(
            self._get_url(business_id, resource_id), HttpVerbs.PUT, data={self.single_name: data}
        )
        return Result(self.single_name, response)

    def delete(self, business_id: int, resource_id: int) -> Result:
        response = self._request(self._get_url(business_id, resource_id), HttpVerbs.DELETE)
        return Result(self.single_name, response)
