import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks.client import API_BASE_URL

SERVICE_PAYLOAD = {
    "business_id": 98765,
    "id": 12345,
    "name": "A new service",
    "billable": True,
    "project_default": False,
    "vis_state": 0
}


class TestCommentsResources:
    def setup_method(self, method):
        self.business_id = 98765
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_get_service(self):
        service_id = 12345
        service_response = {
            "service": SERVICE_PAYLOAD
        }
        url = "{}/comments/business/{}/service/{}".format(API_BASE_URL, self.business_id, service_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(service_response),
            status=200
        )

        service = self.freshBooksClient.services.get(self.business_id, service_id)

        assert str(service) == "Result(service)"
        assert service.name == "A new service"
        assert service.data["billable"] is True
        assert service.billable is True
        assert service.id == service_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_list_services(self):
        services_response = {
            "services": [
                SERVICE_PAYLOAD, SERVICE_PAYLOAD
            ],
            "meta": {
                "total": 2,
                "per_page": 50,
                "page": 1,
                "pages": 1
            }
        }
        url = "{}/comments/business/{}/services".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(services_response),
            status=200
        )

        services = self.freshBooksClient.services.list(self.business_id)
        assert str(services) == "ListResult(services)"
        assert len(services) == 2
        assert services.pages.total == 2
        assert services[0].name == "A new service"
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_create_service(self):
        service_response = {
            "service": SERVICE_PAYLOAD
        }
        url = "{}/comments/business/{}/service".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(service_response),
            status=200
        )

        payload = {
            "name": "A new service",
            "billable": True,
        }
        service = self.freshBooksClient.services.create(self.business_id, payload)

        assert str(service) == "Result(service)"
        assert service.name == "A new service"
        assert service.data["billable"] is True
        assert service.billable is True
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"
