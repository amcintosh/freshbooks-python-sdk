import json
from datetime import date, datetime, timezone

import httpretty
from freshbooks import Client as FreshBooksClient
from freshbooks import FilterBuilder, FreshBooksError, IncludesBuilder, PaginateBuilder
from freshbooks.client import API_BASE_URL

from tests import get_fixture


class TestProjectsResources:
    def setup_method(self, method):
        self.business_id = 98765
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token", auto_retry=False)

    @httpretty.activate
    def test_get_project(self):
        project_id = 654321
        url = "{}/projects/business/{}/project/{}".format(API_BASE_URL, self.business_id, project_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_project_response")),
            status=200
        )

        project = self.freshBooksClient.projects.get(self.business_id, project_id)

        assert str(project) == "Result(project)"
        assert project.data["title"] == "Awesome Project"
        assert project.title == "Awesome Project"
        assert project.id == project_id
        assert project.vis_state is None, "Projects use active, not vis_state"
        assert project.data["updated_at"] == "2020-09-13T03:10:13"
        assert project.updated_at == datetime(
            year=2020, month=9, day=13, hour=3, minute=10, second=13, tzinfo=timezone.utc
        )
        assert project.data["due_date"] == "2021-01-02"
        assert project.due_date == date(year=2021, month=1, day=2)

        for service in project.services:
            assert service.billable is True
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"

    @httpretty.activate
    def test_get_project__includes(self):
        project_id = 654321
        url = "{}/projects/business/{}/project/{}".format(API_BASE_URL, self.business_id, project_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_project_response")),
            status=200
        )

        includes = IncludesBuilder()
        includes.include("include_logged_duration")

        project = self.freshBooksClient.projects.get(self.business_id, project_id, includes=includes)

        expected_params = {
            "include_logged_duration": ['true']
        }

        assert str(project) == "Result(project)"
        assert project.title == "Awesome Project"
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_get_project__not_found(self):
        project_id = 654321
        url = "{}/projects/business/{}/project/{}".format(API_BASE_URL, self.business_id, project_id)
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
        url = "{}/projects/business/{}/project/{}".format(API_BASE_URL, self.business_id, project_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="stuff",
            status=500
        )

        try:
            self.freshBooksClient.projects.get(self.business_id, project_id)
        except FreshBooksError as e:
            assert str(e) == "Failed to parse response"
            assert e.status_code == 500
            assert e.raw_response == "stuff"

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

        assert str(projects) == "ListResult(projects)"
        assert len(projects) == 3
        assert projects.pages.total == 3
        assert projects.data["meta"]["total"] == 3
        assert projects.data["projects"][0]["id"] == project_ids[0]
        for index, project in enumerate(projects):
            assert project.id == project_ids[index]
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"

    @httpretty.activate
    def test_list_projects__paged(self):
        url = "{}/projects/business/{}/projects?page=2&per_page=1".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_projects_response")),
            status=200
        )

        p = PaginateBuilder(2, 1)
        self.freshBooksClient.projects.list(self.business_id, builders=[p])

        expected_params = {"page": ["2"], "per_page": ["1"]}
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_list_projects__filtered(self):
        url = "{}/projects/business/{}/projects?page=2&per_page=1".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_projects_response")),
            status=200
        )

        filter = FilterBuilder()
        filter.boolean("active", True)
        self.freshBooksClient.projects.list(self.business_id, builders=[filter])

        expected_params = {"active": ["True"]}
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_create_project(self):
        url = "{}/projects/business/{}/project".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("create_project_response")),
            status=200
        )

        payload = {
            "title": "Some Project",
            "client_id": "56789",
            "project_type": "fixed_price",
            "fixed_price": "600"
        }
        project = self.freshBooksClient.projects.create(self.business_id, payload)

        assert str(project) == "Result(project)"
        assert project.id == 12345
        assert project.title == "Some Project"
        assert project.data["title"] == "Some Project"
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_create_project__validation_errors(self):
        response = get_fixture("create_project__validation_errors")
        url = "{}/projects/business/{}/project".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(response),
            status=422
        )

        try:
            self.freshBooksClient.projects.create(self.business_id, {})
        except FreshBooksError as e:
            assert str(e) == "Error: title field required"
            assert e.status_code == 422
            assert e.error_code == 2001
            assert e.error_details == [
                {"description": "field required"},
                {"title": "field required"}
            ]
            assert e.raw_response == response

    @httpretty.activate
    def test_update_project(self):
        project_id = 12345
        url = "{}/projects/business/{}/project/{}".format(API_BASE_URL, self.business_id, project_id)
        httpretty.register_uri(
            httpretty.PUT,
            url,
            body=json.dumps(get_fixture("create_project_response")),
            status=200
        )

        payload = {
            "title": "Some Project",
            "client_id": "56789",
            "project_type": "fixed_price",
            "fixed_price": "600"
        }
        project = self.freshBooksClient.projects.update(self.business_id, project_id, payload)

        assert str(project) == "Result(project)"
        assert project.id == 12345
        assert project.title == "Some Project"
        assert project.data["title"] == "Some Project"
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_delete_project(self):
        project_id = 654321
        url = "{}/projects/business/{}/project/{}".format(API_BASE_URL, self.business_id, project_id)
        httpretty.register_uri(httpretty.DELETE, url, status=204)

        tax = self.freshBooksClient.projects.delete(self.business_id, project_id)

        assert str(tax) == "Result(project)"
        assert tax.data == {}
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert httpretty.last_request().body == b""
