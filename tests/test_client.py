from datetime import datetime
import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError
from freshbooks.client import API_BASE_URL
from tests import get_fixture


class TestClientAuth:
    def setup_method(self, method):
        self.freshBooksClient = FreshBooksClient(client_id="some_client", redirect_uri="https://example.com")

    def test_get_auth_request_url(self):
        auth_url = self.freshBooksClient.get_auth_request_url()
        assert (
            auth_url == "https://auth.freshbooks.com/service/auth/oauth/authorize?"
            "client_id=some_client&response_type=code&redirect_uri=https%3A%2F%2Fexample.com"
        )

    def test_get_auth_request_url__with_scopes(self):
        scopes = ["some:scope", "another:scope"]
        auth_url = self.freshBooksClient.get_auth_request_url(scopes)
        assert (
            auth_url == "https://auth.freshbooks.com/service/auth/oauth/authorize?"
            "client_id=some_client&response_type=code&redirect_uri=https%3A%2F%2Fexample.com"
            "&scope=some%3Ascope+another%3Ascope"
        )

    @httpretty.activate
    def test_get_access_token(self):
        url = "{}/auth/oauth/token".format(API_BASE_URL)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("auth_token_response")),
            status=200
        )

        result = self.freshBooksClient.get_access_token("some_grant")

        assert httpretty.last_request().body == (
            "client_id=some_client&grant_type=authorization_code"
            "&redirect_uri=https%3A%2F%2Fexample.com&code=some_grant").encode("utf-8")
        assert self.freshBooksClient.access_token == "my_access_token"
        assert result.access_token == "my_access_token"
        assert self.freshBooksClient.refresh_token == "my_refresh_token"
        assert result.refresh_token == "my_refresh_token"
        assert self.freshBooksClient.access_token_expires_at == datetime(2010, 10, 17)
        assert result.access_token_expires_at == datetime(2010, 10, 17)

    @httpretty.activate
    def test_get_access_token__failure(self):
        url = "{}/auth/oauth/token".format(API_BASE_URL)
        httpretty.register_uri(httpretty.POST, url, status=500)

        try:
            self.freshBooksClient.get_access_token("some_grant")
        except FreshBooksError as e:
            assert str(e) == "Failed to fetch access_token"
            assert e.status_code == 500

    @httpretty.activate
    def test_get_refresh_token(self):
        self.freshBooksClient = FreshBooksClient(
            client_id="some_client",
            redirect_uri="https://example.com",
            access_token="an_old_token",
            refresh_token="an_old_refresh_token"
        )
        url = "{}/auth/oauth/token".format(API_BASE_URL)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("auth_token_response")),
            status=200
        )

        result = self.freshBooksClient.refresh_access_token()

        assert httpretty.last_request().body == (
            "client_id=some_client&grant_type=refresh_token"
            "&redirect_uri=https%3A%2F%2Fexample.com&refresh_token=an_old_refresh_token").encode("utf-8")
        assert self.freshBooksClient.access_token == "my_access_token"
        assert result.access_token == "my_access_token"
        assert self.freshBooksClient.refresh_token == "my_refresh_token"
        assert result.refresh_token == "my_refresh_token"
        assert self.freshBooksClient.access_token_expires_at == datetime(2010, 10, 17)
        assert result.access_token_expires_at == datetime(2010, 10, 17)

    @httpretty.activate
    def test_get_refresh_token__uninitialized_client(self):
        url = "{}/auth/oauth/token".format(API_BASE_URL)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("auth_token_response")),
            status=200
        )

        result = self.freshBooksClient.refresh_access_token("an_old_refresh_token")

        assert httpretty.last_request().body == (
            "client_id=some_client&grant_type=refresh_token"
            "&redirect_uri=https%3A%2F%2Fexample.com&refresh_token=an_old_refresh_token").encode("utf-8")
        assert self.freshBooksClient.access_token == "my_access_token"
        assert result.access_token == "my_access_token"
        assert self.freshBooksClient.refresh_token == "my_refresh_token"
        assert result.refresh_token == "my_refresh_token"
        assert self.freshBooksClient.access_token_expires_at == datetime(2010, 10, 17)
        assert result.access_token_expires_at == datetime(2010, 10, 17)
