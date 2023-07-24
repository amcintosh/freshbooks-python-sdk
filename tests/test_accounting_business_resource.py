import json
from datetime import datetime, timezone

import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks.client import API_BASE_URL, VERSION
from freshbooks.errors import FreshBooksError
from tests import get_fixture
from freshbooks.api.accounting_business import AccountingBusinessResource


class TestAccountingBusinessResources:
    def setup_method(self, method):
        self.business_uuid = "a_business_uuid"
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_get_ledger_account(self):
        account_uuid = "a_uuid"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts/{}".format(
            API_BASE_URL, self.business_uuid, account_uuid
        )
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_ledger_account_response")),
            status=200
        )

        account = self.freshBooksClient.ledger_accounts.get(self.business_uuid, account_uuid)

        assert str(account) == "Result(accounts)"
        assert account.uuid == account_uuid
        assert account.data["name"] == "Cash"
        assert account.name == "Cash"
        assert account.number == "1000"
        assert account.description == "As described"
        assert account.type == "asset"
        assert account.sub_type == "Cash & Bank"
        assert account.system_account_name == "Cash"
        assert account.parent_account is None
        assert account.sub_accounts[0] == "a_uuid2"
        assert account.auto_created is True
        assert account.state == "active"
        assert account.data["updated_at"] == "2023-04-27T14:33:48.841075Z"
        assert account.updated_at == datetime(
            year=2023, month=4, day=27, hour=14, minute=33, second=48, microsecond=841075, tzinfo=timezone.utc
        )

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert (httpretty.last_request().headers["user-agent"]
                == f"FreshBooks python sdk/{VERSION} client_id some_client")

    @httpretty.activate
    def test_get_ledger_account__not_found(self):
        account_uuid = "a_uuid"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts/{}".format(
            API_BASE_URL, self.business_uuid, account_uuid
        )
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_ledger_account_response__not_found")),
            status=404
        )
        try:
            self.freshBooksClient.ledger_accounts.get(self.business_uuid, account_uuid)
        except FreshBooksError as e:
            assert str(e) == "Not found."
            assert e.status_code == 404
            assert e.error_details == [
                {"message": "Not found.", "field": None}
            ]

    @httpretty.activate
    def test_get_ledger_account__bad_response(self):
        account_uuid = "a_uuid"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts/{}".format(
            API_BASE_URL, self.business_uuid, account_uuid
        )
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="stuff",
            status=500
        )
        try:
            self.freshBooksClient.ledger_accounts.get(self.business_uuid, account_uuid)
        except FreshBooksError as e:
            assert str(e) == "Failed to parse response"
            assert e.status_code == 500
            assert e.raw_response == "stuff"

    @httpretty.activate
    def test_get_ledger_account__missing_response_data(self):
        account_uuid = "a_uuid"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts/{}".format(
            API_BASE_URL, self.business_uuid, account_uuid
        )
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps({"foo": "bar"}),
            status=200
        )
        try:
            self.freshBooksClient.ledger_accounts.get(self.business_uuid, account_uuid)
        except FreshBooksError as e:
            assert str(e) == "Returned an unexpected response"
            assert e.status_code == 200
            assert e.raw_response == "{\"foo\": \"bar\"}"

    @httpretty.activate
    def test_list_ledger_accounts(self):
        freshBooksClient = FreshBooksClient(
            client_id="some_client", access_token="some_token", user_agent="phone_home"
        )
        account_ids = ["a_uuid", "a_uuid2"]
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts".format(API_BASE_URL, self.business_uuid)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_ledger_accounts_response")),
            status=200
        )

        accounts = freshBooksClient.ledger_accounts.list(self.business_uuid)

        assert str(accounts) == "ListResult(accounts)"
        assert len(accounts) == 2
        assert accounts.pages is None
        assert accounts[0].uuid == account_ids[0]
        assert accounts[1].uuid == account_ids[1]
        for index, account in enumerate(accounts):
            assert account.uuid == account_ids[index]
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert httpretty.last_request().headers["user-agent"] == "phone_home"

    @httpretty.activate
    def test_list_ledger_account__no_accounts(self):
        empty_results = {
            "data": []
        }
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts".format(API_BASE_URL, self.business_uuid)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(empty_results),
            status=200
        )

        accounts = self.freshBooksClient.ledger_accounts.list(self.business_uuid)

        assert str(accounts) == "ListResult(accounts)"
        assert len(accounts) == 0
        assert accounts.pages is None

    @httpretty.activate
    def test_create_ledger_account(self):
        account_uuid = "a_uuid"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts".format(
            API_BASE_URL, self.business_uuid
        )
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("get_ledger_account_response")),
            status=200
        )

        payload = {
            "name": "Cash",
            "number": "1000",
            "description": "As described"
        }
        account = self.freshBooksClient.ledger_accounts.create(self.business_uuid, payload)

        assert str(account) == "Result(accounts)"
        assert account.uuid == account_uuid
        assert account.data["name"] == "Cash"
        assert account.name == "Cash"
        assert account.number == "1000"
        assert account.description == "As described"
        assert account.type == "asset"
        assert account.sub_type == "Cash & Bank"
        assert account.system_account_name == "Cash"
        assert account.parent_account is None
        assert account.sub_accounts[0] == "a_uuid2"
        assert account.auto_created is True
        assert account.state == "active"
        assert account.data["updated_at"] == "2023-04-27T14:33:48.841075Z"
        assert account.updated_at == datetime(
            year=2023, month=4, day=27, hour=14, minute=33, second=48, microsecond=841075, tzinfo=timezone.utc
        )

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_create_ledger_account__validation_errors(self):
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts".format(
            API_BASE_URL, self.business_uuid
        )
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("create_ledger_account_response__validation_errors")),
            status=400
        )

        payload = {
            "description": "As described"
        }

        try:
            self.freshBooksClient.ledger_accounts.create(self.business_uuid, payload)
        except FreshBooksError as e:
            assert str(e) == "parent_account: This field is required."
            assert e.status_code == 400
            assert e.error_details == [
                {"message": "This field is required.", "field": "name"},
                {"message": "This field is required.", "field": "sub_type"},
                {"message": "This field is required.", "field": "parent_account"}
            ]

    @httpretty.activate
    def test_update_ledger_account(self):
        account_uuid = "a_uuid"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts/{}".format(
            API_BASE_URL, self.business_uuid, account_uuid
        )
        httpretty.register_uri(
            httpretty.PUT,
            url,
            body=json.dumps(get_fixture("get_ledger_account_response")),
            status=200
        )

        payload = {
            "name": "Cash",
            "number": "1000",
            "description": "As described"
        }
        account = self.freshBooksClient.ledger_accounts.update(self.business_uuid, account_uuid, payload)

        assert str(account) == "Result(accounts)"
        assert account.uuid == account_uuid
        assert account.data["name"] == "Cash"
        assert account.name == "Cash"
        assert account.number == "1000"

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"

    @httpretty.activate
    def test_delete_update_ledger_account(self):
        """Note, there is no DELETE on ledger accounts.
        This test overrides that to tes the functionality on the base resource level.
        This is neccessary as there are currently no other resources with DELETE using this base.
        """
        account_uuid = "a_uuid"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts/{}".format(
            API_BASE_URL, self.business_uuid, account_uuid
        )
        httpretty.register_uri(
            httpretty.DELETE,
            url,
            body=json.dumps(get_fixture("get_ledger_account_response")),
            status=204
        )

        overriden_resource = AccountingBusinessResource(
            self.freshBooksClient._client_resource_config(), "ledger_accounts/accounts", "accounts"
        )
        account = overriden_resource.delete(self.business_uuid, account_uuid)

        assert str(account) == "Result(accounts)"
        assert account.data == {}
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert httpretty.last_request().body == b""
