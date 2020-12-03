import json
import httpretty

from freshbooks import Client as FreshBooksClient, FreshBooksError
from freshbooks.client import API_BASE_URL
from tests import get_fixture


class TestAuthResources:
    def setup_method(self, method):
        self.business_id = 98765
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_get_me(self):
        url = "{}/auth/api/v1/users/me".format(API_BASE_URL)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("auth_me_response")),
            status=200
        )

        current_user = self.freshBooksClient.current_user

        assert str(current_user) == "Identity(12345, skovalic@cis.com)"
        assert current_user.identity_id == 12345
        assert current_user.full_name == "Simon Kovalic"
        assert current_user.email == "skovalic@cis.com"
        assert current_user.data["email"] == "skovalic@cis.com"
        assert len(current_user.business_memberships) == 2
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"

    @httpretty.activate
    def test_get_me__not_authorized(self):
        url = "{}/auth/api/v1/users/me".format(API_BASE_URL)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("auth_me_response__no_auth")),
            status=403
        )

        try:
            self.freshBooksClient.current_user
        except FreshBooksError as e:
            assert str(e) == "This action requires authentication to continue."
            assert e.status_code == 403
            assert e.error_code == "unauthenticated"

    @httpretty.activate
    def test_get_me__bad_response(self):
        url = "{}/auth/api/v1/users/me".format(API_BASE_URL)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="stuff",
            status=500
        )

        try:
            self.freshBooksClient.current_user
        except FreshBooksError as e:
            assert str(e) == "Failed to parse response"
            assert e.status_code == 500
            assert e.raw_response == "stuff"

    @httpretty.activate
    def test_get_me__unknown_response(self):
        url = "{}/auth/api/v1/users/me".format(API_BASE_URL)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="{\"foo\": \"bar\"}",
            status=200
        )

        try:
            self.freshBooksClient.current_user
        except FreshBooksError as e:
            assert str(e) == "Returned an unexpected response"
            assert e.status_code == 200
            assert e.raw_response == "{\"foo\": \"bar\"}"
