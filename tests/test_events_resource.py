import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks import PaginateBuilder, FilterBuilder, FreshBooksError
from freshbooks.client import API_BASE_URL, VERSION
from tests import get_fixture


class TestEventsResources:
    def setup_method(self, method):
        self.account_id = "ACM123"
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_get_callback(self):
        callback_id = 123
        url = "{}/events/account/{}/events/callbacks/{}".format(API_BASE_URL, self.account_id, callback_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_callback_response")),
            status=200
        )

        callback = self.freshBooksClient.callbacks.get(self.account_id, callback_id)

        assert str(callback) == "Result(callback)"
        assert callback.callbackid == 123
        assert callback.data["callbackid"] == 123

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert (httpretty.last_request().headers["user-agent"]
                == f"FreshBooks python sdk/{VERSION} client_id some_client")

    @httpretty.activate
    def test_get_callback__not_found(self):
        callback_id = 123
        url = "{}/events/account/{}/events/callbacks/{}".format(API_BASE_URL, self.account_id, callback_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_callback_response__not_found")),
            status=404
        )
        try:
            self.freshBooksClient.callbacks.get(self.account_id, callback_id)
        except FreshBooksError as e:
            assert str(e) == "Requested resource could not be found."
            assert e.status_code == 404
            assert e.error_code == 404
            assert e.raw_response == {"errno": 404, "message": "Requested resource could not be found."}

    @httpretty.activate
    def test_get_callback__bad_response(self):
        callback_id = 123
        url = "{}/events/account/{}/events/callbacks/{}".format(API_BASE_URL, self.account_id, callback_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="stuff",
            status=500
        )
        try:
            self.freshBooksClient.callbacks.get(self.account_id, callback_id)
        except FreshBooksError as e:
            assert str(e) == "Failed to parse response"
            assert e.status_code == 500
            assert e.raw_response == "stuff"

    @httpretty.activate
    def test_get_callback__missing_response(self):
        callback_id = 123
        url = "{}/events/account/{}/events/callbacks/{}".format(API_BASE_URL, self.account_id, callback_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps({"foo": "bar"}),
            status=200
        )
        try:
            self.freshBooksClient.callbacks.get(self.account_id, callback_id)
        except FreshBooksError as e:
            assert str(e) == "Returned an unexpected response"
            assert e.status_code == 200
            assert e.raw_response == "{\"foo\": \"bar\"}"

    @httpretty.activate
    def test_list_callback(self):
        callback_ids = [123, 124, 125]
        url = "{}/events/account/{}/events/callbacks".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_callbacks_response")),
            status=200
        )

        callbacks = self.freshBooksClient.callbacks.list(self.account_id)

        assert str(callbacks) == "ListResult(callbacks)"
        assert callbacks.name == "callbacks"
        assert len(callbacks) == 3
        assert callbacks.pages.total == 3
        for index, callback in enumerate(callbacks):
            assert callback.callbackid == callback_ids[index]
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_list_callbacks__paged(self):
        url = "{}/events/account/{}/events/callbacks?page=2&per_page=1".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_callbacks_response")),
            status=200
        )

        p = PaginateBuilder(2, 1)
        self.freshBooksClient.callbacks.list(self.account_id, builders=[p])

        expected_params = {"page": ["2"], "per_page": ["1"]}
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_list_callbacks__filtered(self):
        url = (
            "{}/events/account/{}/events/callbacks?search[event]=estimate.create"
        ).format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_callbacks_response")),
            status=200
        )

        filter = FilterBuilder()
        filter.equals("event", "estimate.create")

        self.freshBooksClient.callbacks.list(self.account_id, builders=[filter])

        expected_params = {"search[event]": ["estimate.create"]}
        assert httpretty.last_request().querystring == expected_params

    @httpretty.activate
    def test_create_callback(self):
        url = "{}/events/account/{}/events/callbacks".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("get_callback_response")),
            status=200
        )

        payload = {"event": "invoice.create", "uri": "http://somewhere.test"}
        callback = self.freshBooksClient.callbacks.create(self.account_id, payload)

        assert str(callback) == "Result(callback)"
        assert callback.event == "invoice.create"
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_update_callback(self):
        callback_id = 123
        url = "{}/events/account/{}/events/callbacks/{}".format(API_BASE_URL, self.account_id, callback_id)
        httpretty.register_uri(
            httpretty.PUT,
            url,
            body=json.dumps(get_fixture("get_callback_response")),
            status=200
        )

        payload = {"event": "invoice.create"}
        callback = self.freshBooksClient.callbacks.update(self.account_id, callback_id, payload)

        assert str(callback) == "Result(callback)"
        assert callback.event == "invoice.create"
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_resend_verification_callback(self):
        callback_id = 123
        url = "{}/events/account/{}/events/callbacks/{}".format(API_BASE_URL, self.account_id, callback_id)
        httpretty.register_uri(
            httpretty.PUT,
            url,
            body=json.dumps(get_fixture("get_callback_response")),
            status=200
        )

        callback = self.freshBooksClient.callbacks.resend_verification(self.account_id, callback_id)

        assert str(callback) == "Result(callback)"
        assert callback.event == "invoice.create"
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_verify_callback(self):
        callback_id = 123
        url = "{}/events/account/{}/events/callbacks/{}".format(API_BASE_URL, self.account_id, callback_id)
        httpretty.register_uri(
            httpretty.PUT,
            url,
            body=json.dumps(get_fixture("get_callback_response")),
            status=200
        )

        callback = self.freshBooksClient.callbacks.verify(self.account_id, callback_id, "some_code")

        assert str(callback) == "Result(callback)"
        assert callback.event == "invoice.create"
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_delete_callback(self):
        url = "{}/events/account/{}/events/callbacks/{}".format(API_BASE_URL, self.account_id, 123)
        httpretty.register_uri(httpretty.DELETE, url, body="{\"response\": {}}", status=204)

        callback = self.freshBooksClient.callbacks.delete(self.account_id, 123)

        assert str(callback) == "Result(callback)"
        assert callback.data == {}
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert httpretty.last_request().body == b""
