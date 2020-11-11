import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError
from freshbooks.client import API_BASE_URL
from tests import get_fixture


class TestClientResources:
    def setup_method(self, method):
        self.business_id = 98765
        self.freshBooksClient = FreshBooksClient(access_token="some_token")

    @httpretty.activate
    def test_get_project(self):
        project_id = 654321
        url = "{}/projects/business/{}/projects/{}".format(API_BASE_URL, self.business_id, project_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_project_response")),
            status=200
        )

        project = self.freshBooksClient.projects.get(self.business_id, project_id)

        assert project.name == "project"
        assert project.data["title"] == "Awesome Project"
        assert project.title == "Awesome Project"
        assert project.id == project_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"

    @httpretty.activate
    def test_get_project__not_found(self):
        project_id = 654321
        url = "{}/projects/business/{}/projects/{}".format(API_BASE_URL, self.business_id, project_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_project_response__not_found")),
            status=404
        )

        try:
            self.freshBooksClient.projects.get(self.business_id, project_id)
        except FreshBooksError as e:
            assert str(e) == "Requested resource could not be found."
            assert e.status_code == 404
            assert e.error_code is None
