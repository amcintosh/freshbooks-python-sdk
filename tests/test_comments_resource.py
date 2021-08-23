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

SERVICE_RATE_PAYLOAD = {
    "rate": "10.00",
    "service_id": 12345,
    "business_id": 98765
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


class TestCommentsSubResources:
    def setup_method(self, method):
        self.business_id = 98765
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_get_service_rate(self):
        """Important test vs test_get_service as this uses a sub-resource path.
        Eg. /service/<id> vs /service/<id>/rate
        """
        service_id = 12345
        service_response = {
            "service_rate": SERVICE_RATE_PAYLOAD
        }
        url = "{}/comments/business/{}/service/{}/rate".format(API_BASE_URL, self.business_id, service_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(service_response),
            status=200
        )

        service_rate = self.freshBooksClient.service_rates.get(self.business_id, service_id)

        assert str(service_rate) == "Result(service_rate)"
        assert service_rate.rate == "10.00"
        assert service_rate.service_id == service_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_list_service_rates(self):
        service_rates_response = {
            "service_rates": [
                SERVICE_RATE_PAYLOAD, SERVICE_RATE_PAYLOAD
            ]
        }
        url = "{}/comments/business/{}/service_rates".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(service_rates_response),
            status=200
        )

        service_rates = self.freshBooksClient.service_rates.list(self.business_id)
        assert str(service_rates) == "ListResult(service_rates)"
        assert len(service_rates) == 2
        assert service_rates.pages is None, "service_rates is not a paginated resource"
        assert service_rates[0].rate == "10.00"
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_create_service_rate(self):
        service_id = 12345
        service_rate_response = {
            "service_rate": SERVICE_RATE_PAYLOAD
        }
        url = "{}/comments/business/{}/service/{}/rate".format(API_BASE_URL, self.business_id, service_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(service_rate_response),
            status=200
        )

        payload = {
            "rate": "10.00",
        }
        service_rate = self.freshBooksClient.service_rates.create(self.business_id, service_id, payload)

        assert str(service_rate) == "Result(service_rate)"
        assert service_rate.rate == "10.00"
        assert service_rate.service_id == service_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"
