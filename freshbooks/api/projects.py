from freshbooks.errors import FailedRequest, FreshBooksError
from freshbooks.api.resource import Resource, HttpVerbs
from freshbooks.models import Result
from decimal import Decimal


class ProjectsResource(Resource):
    def __init__(self, base_url, access_token, project_path, single_name, list_name=None):
        super().__init__(base_url, access_token)
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
        if status == 200 and method == HttpVerbs.HEAD:
            # no content returned from a HEAD
            return

        try:
            content = response.json(parse_float=Decimal)
        except ValueError:
            raise FailedRequest(status, "Failed to parse response", raw_response=response.text)

        if status >= 400:
            code = content.get("errno")
            message = content.get("error", "Unknown error")
            raise FreshBooksError(status, message, error_code=code, raw_response=content)
        return content

    def get(self, business_id, resource_id):
        data = self._request(self._get_url(business_id, resource_id), HttpVerbs.GET)
        return Result(self.single_name, data)
