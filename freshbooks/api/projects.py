from freshbooks.errors import FreshBooksError
from freshbooks.api.resource import Resource, HttpVerbs
from freshbooks.models import Result, ListResult
from decimal import Decimal


class ProjectsResource(Resource):
    def __init__(self, client_config, project_path, single_name, list_name=None):
        super().__init__(client_config)
        self.project_path = project_path
        self.single_name = single_name
        self.list_name = list_name
        if not list_name:
            self.list_name = project_path

    def _get_url(self, business_id, resource_id=None):
        if resource_id:
            return "{}/projects/business/{}/{}/{}".format(self.base_url, business_id, self.project_path, resource_id)
        return "{}/projects/business/{}/{}".format(self.base_url, business_id, self.project_path)

    def _request(self, url, method, data=None):
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
            code = content.get("errno")
            message = content.get("error", "Unknown error")
            raise FreshBooksError(status, message, error_code=code, raw_response=content)
        return content

    def get(self, business_id, resource_id):
        data = self._request(self._get_url(business_id, resource_id), HttpVerbs.GET)
        return Result(self.single_name, data)

    def list(self, business_id, builders=None):
        resource_url = self._get_url(business_id)
        query_string = self._build_query_string(builders)
        data = self._request(f"{resource_url}{query_string}", HttpVerbs.GET)
        return ListResult(self.list_name, self.single_name, data)

    def create(self, business_id, data):
        response = self._request(self._get_url(business_id), HttpVerbs.POST, data={self.single_name: data})
        return Result(self.single_name, response)

    def update(self, business_id, resource_id, data):
        response = self._request(
            self._get_url(business_id, resource_id), HttpVerbs.PUT, data={self.single_name: data}
        )
        return Result(self.single_name, response)
