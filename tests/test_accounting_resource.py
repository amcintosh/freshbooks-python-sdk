from datetime import datetime, timezone
import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks import PaginateBuilder, FilterBuilder, IncludesBuilder, FreshBooksError, VisState
from freshbooks.client import API_BASE_URL, VERSION
from tests import get_fixture


class TestAccountingResources:
    def setup_method(self, method):
        self.account_id = "ACM123"
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

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

        assert str(client) == "Result(client)"
        assert client.userid == client_id
        assert client.data["organization"] == "American Cyanamid"
        assert client.organization == "American Cyanamid"
        assert client.data["updated"] == "2020-11-01 13:11:10"
        assert client.updated == datetime(
            year=2020, month=11, day=1, hour=18, minute=11, second=10, tzinfo=timezone.utc
        )

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert (httpretty.last_request().headers["user-agent"]
                == f"FreshBooks python sdk/{VERSION} client_id some_client")

    @httpretty.activate
    def test_get_client__with_version(self):
        client_id = 12345
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_client_response")),
            status=200
        )
        API_VERSION = "2023-02-20"

        freshBooksClient = FreshBooksClient(
            client_id="some_client", access_token="some_token", api_version=API_VERSION
        )
        client = freshBooksClient.clients.get(self.account_id, client_id)

        assert str(client) == "Result(client)"
        assert client.userid == client_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert httpretty.last_request().headers["X-API-VERSION"] == API_VERSION

    @httpretty.activate
    def test_get_client__includes(self):
        client_id = 12345
        url = "{}/accounting/account/{}/users/clients/{}?include[]=late_reminders&include[]=last_activity".format(
            API_BASE_URL, self.account_id, client_id
        )
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_client_response")),
            status=200
        )

        includes = IncludesBuilder()
        includes.include("late_reminders").include("last_activity")

        client = self.freshBooksClient.clients.get(self.account_id, client_id, includes=includes)

        expected_params = {
            "include[]": ["late_reminders", "last_activity"]
        }
        assert str(client) == "Result(client)"
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_get_client__sub_lists(self):
        client_id = 12345
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_client_response")),
            status=200
        )

        client = self.freshBooksClient.clients.get(self.account_id, client_id)

        assert str(client) == "Result(client)"
        assert str(client.outstanding_balance) == "ListResult(outstanding_balance)"
        assert client.data["outstanding_balance"][0]["amount"] == {"amount": 10, "code": "CAD"}

        assert str(client.outstanding_balance[0]) == "Result(outstanding_balance)"
        assert client.outstanding_balance[0].data == {"amount": {"amount": 10, "code": "CAD"}}
        assert client.outstanding_balance[0].amount.code == "CAD"

        for balance in client.outstanding_balance:
            assert balance.amount.code == "CAD"

        assert str(client.test_amount) == "Result(test_amount)"
        assert client.test_amount.code == "CAD"
        assert client.grand_total_balance == []

    @httpretty.activate
    def test_get_client__not_found_error(self):
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
            assert e.error_details == [{
                "errno": 1012,
                "field": "userid",
                "message": "Client not found.",
                "object": "client",
                "value": "12345"
            }]

    @httpretty.activate
    def test_get_client__bad_response(self):
        client_id = 12345
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="stuff",
            status=500
        )
        try:
            self.freshBooksClient.clients.get(self.account_id, client_id)
        except FreshBooksError as e:
            assert str(e) == "Failed to parse response"
            assert e.status_code == 500
            assert e.raw_response == "stuff"

    @httpretty.activate
    def test_get_client__missing_response(self):
        client_id = 12345
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps({"foo": "bar"}),
            status=200
        )
        try:
            self.freshBooksClient.clients.get(self.account_id, client_id)
        except FreshBooksError as e:
            assert str(e) == "Returned an unexpected response"
            assert e.status_code == 200
            assert e.raw_response == "{\"foo\": \"bar\"}"

    @httpretty.activate
    def test_list_clients(self):
        freshBooksClient = FreshBooksClient(
            client_id="some_client", access_token="some_token", user_agent="phone_home"
        )
        client_ids = [12345, 12346, 12457]
        url = "{}/accounting/account/{}/users/clients".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_clients_response")),
            status=200
        )

        clients = freshBooksClient.clients.list(self.account_id)

        assert str(clients) == "ListResult(clients)"
        assert len(clients) == 3
        assert clients.pages.total == 3
        assert clients.data["total"] == 3
        assert clients[0].userid == client_ids[0]
        assert clients.data["clients"][0]["userid"] == client_ids[0]
        for index, client in enumerate(clients):
            assert client.userid == client_ids[index]
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert httpretty.last_request().headers["user-agent"] == "phone_home"

    @httpretty.activate
    def test_list_clients__no_matching_clients(self):
        empty_results = {
            "response": {
                "result": {
                    "clients": [],
                    "page": 1,
                    "pages": 0,
                    "per_page": 15,
                    "total": 0
                }
            }
        }
        url = "{}/accounting/account/{}/users/clients".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(empty_results),
            status=200
        )

        clients = self.freshBooksClient.clients.list(self.account_id)

        assert clients.data["total"] == 0
        assert clients.data["clients"] == []

    @httpretty.activate
    def test_list_clients__paged(self):
        url = "{}/accounting/account/{}/users/clients?page=2&per_page=1".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_clients_response")),
            status=200
        )

        p = PaginateBuilder(2, 1)
        self.freshBooksClient.clients.list(self.account_id, builders=[p])

        expected_params = {"page": ["2"], "per_page": ["1"]}
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_list_clients__filtered(self):
        url = ("{}/accounting/account/{}/users/clients?search[userids][]=1&search[userids][]=2"
               "&search[date_min]=2010-10-17&search[date_max]=2012-11-21").format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_clients_response")),
            status=200
        )

        date_min = datetime(year=2010, month=10, day=17, hour=5, minute=47)
        date_max = datetime(year=2012, month=11, day=21, hour=12, minute=34)
        filter = FilterBuilder()
        filter.in_list("userid", [1, 2])

        filter.between("date", min=date_min, max=date_max)
        self.freshBooksClient.clients.list(self.account_id, builders=[filter])

        expected_params = {
            "search[date_max]": ["2012-11-21"],
            "search[date_min]": ["2010-10-17"],
            "search[userids][]": ["1", "2"]}
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_list_clients__includes(self):
        url = (
            "{}/accounting/account/{}/users/clients?include[]=late_reminders&include[]=last_activity"
        ).format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_clients_response")),
            status=200
        )

        includes = IncludesBuilder()
        includes.include("late_reminders").include("last_activity")

        self.freshBooksClient.clients.list(self.account_id, builders=[includes])

        expected_params = {
            "include[]": ["late_reminders", "last_activity"]
        }
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_create_client(self):
        client_id = 56789
        url = "{}/accounting/account/{}/users/clients".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("create_client_response")),
            status=200
        )

        payload = {"email": "john.doe@abcorp.com"}
        client = self.freshBooksClient.clients.create(self.account_id, payload)

        assert str(client) == "Result(client)"
        assert client.data["email"] == "john.doe@abcorp.com"
        assert client.email == "john.doe@abcorp.com"
        assert client.userid == client_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_create_client__includes(self):
        url = "{}/accounting/account/{}/users/clients".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("create_client_response")),
            status=200
        )

        includes = IncludesBuilder()
        includes.include("late_reminders").include("last_activity")

        payload = {"email": "john.doe@abcorp.com"}
        client = self.freshBooksClient.clients.create(self.account_id, payload, includes)

        expected_params = {
            "include[]": ["late_reminders", "last_activity"]
        }
        assert str(client) == "Result(client)"
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_update_client(self):
        client_id = 56789
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(
            httpretty.PUT,
            url,
            body=json.dumps(get_fixture("create_client_response")),
            status=200
        )

        payload = {"email": "john.doe@abcorp.com"}
        client = self.freshBooksClient.clients.update(self.account_id, client_id, payload)

        assert str(client) == "Result(client)"
        assert client.data["email"] == "john.doe@abcorp.com"
        assert client.email == "john.doe@abcorp.com"
        assert client.userid == client_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_update_client__includes(self):
        client_id = 56789
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(
            httpretty.PUT,
            url,
            body=json.dumps(get_fixture("create_client_response")),
            status=200
        )

        includes = IncludesBuilder()
        includes.include("late_reminders").include("last_activity")

        payload = {"email": "john.doe@abcorp.com"}
        client = self.freshBooksClient.clients.update(self.account_id, client_id, payload, includes)

        expected_params = {
            "include[]": ["late_reminders", "last_activity"]
        }
        assert str(client) == "Result(client)"
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_delete__client_via_update(self):
        client_id = 56789
        data = get_fixture("get_client_response")
        data["response"]["result"]["client"]["vis_state"] = 1
        url = "{}/accounting/account/{}/users/clients/{}".format(API_BASE_URL, self.account_id, client_id)
        httpretty.register_uri(httpretty.PUT, url, body=json.dumps(data), status=200)

        client = self.freshBooksClient.clients.delete(self.account_id, client_id)

        assert str(client) == "Result(client)"
        assert client.vis_state == VisState.DELETED
        assert client.vis_state == 1
        assert client.data["vis_state"] == VisState.DELETED
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"
        assert httpretty.last_request().body == "{\"client\": {\"vis_state\": 1}}".encode("utf-8")

    @httpretty.activate
    def test_delete__tax_via_delete(self):
        url = "{}/accounting/account/{}/taxes/taxes/{}".format(API_BASE_URL, self.account_id, 124)
        httpretty.register_uri(httpretty.DELETE, url, body="{\"response\": {}}", status=200)

        tax = self.freshBooksClient.taxes.delete(self.account_id, 124)

        assert str(tax) == "Result(tax)"
        assert tax.data == {}
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert httpretty.last_request().body == b""
