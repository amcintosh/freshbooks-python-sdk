import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError
from freshbooks.client import API_BASE_URL
from tests import get_fixture


class TestClientResources:
    def setup_method(self, method):
        self.account_id = "ACM123"
        self.freshBooksClient = FreshBooksClient(access_token="some_token")

    @httpretty.activate
    def test_get_client(self):
        client_id = 12345
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_client_response")),
            status=200
        )

        client = self.freshBooksClient.clients.get(self.account_id, client_id)

        assert client.name == "client"
        assert client.data["organization"] == "American Cyanamid"
        assert client.organization == "American Cyanamid"
        assert client.userid == client_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"

    @httpretty.activate
    def test_get_client__not_found(self):
        client_id = 12345
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_client_response__not_found")),
            status=404
        )
        try:
            self.freshBooksClient.clients.get(self.account_id, client_id)
        except FreshBooksError as e:
            assert str(e) == "Client not found."
            assert e.status_code == 404
            assert e.error_code == 1012

    @httpretty.activate
    def test_list_clients(self):
        client_ids = [12345, 12346, 12457]
        url = "{}/accounting/account/{}/users/clients".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_clients_response")),
            status=200
        )

        clients = self.freshBooksClient.clients.list(self.account_id)

        assert clients.name == "clients"
        assert clients.data["total"] == 3
        assert clients.data["clients"][0]["userid"] == client_ids[0]
        for index, client in enumerate(clients):
            assert client.userid == client_ids[index]
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
