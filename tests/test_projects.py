import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError, FailedRequest
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

    @httpretty.activate
    def test_get_project__bad_response(self):
        project_id = 654321
        url = "{}/projects/business/{}/projects/{}".format(API_BASE_URL, self.business_id, project_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="stuff",
            status=500
        )

        try:
            self.freshBooksClient.projects.get(self.business_id, project_id)
        except FailedRequest as e:
            assert str(e) == "Failed to parse response: 'stuff'"
            assert e.status_code == 500

    @httpretty.activate
    def test_list_projects(self):
        project_ids = [654321, 654322, 654323]
        url = "{}/projects/business/{}/projects".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_projects_response")),
            status=200
        )

        projects = self.freshBooksClient.projects.list(self.business_id)

        assert projects.name == "projects"
        assert len(projects) == 3
        assert projects.pages.total == 3
        assert projects.data["meta"]["total"] == 3
        assert projects.data["projects"][0]["id"] == project_ids[0]
        for index, project in enumerate(projects):
            assert project.id == project_ids[index]
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"