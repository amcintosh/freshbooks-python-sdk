from datetime import datetime, timezone
import json
import httpretty
import pytest
import uuid

from freshbooks import Client as FreshBooksClient
from freshbooks import PaginateBuilder, FilterBuilder, IncludesBuilder, FreshBooksError, VisState
from freshbooks.client import API_BASE_URL, VERSION
from tests import get_fixture


class TestAccountingBusinessResources:
    def setup_method(self, method):
        self.business_uuid = str(uuid.uuid4())
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_get_ledger_account(self):
        account_uuid = "e17f9556-c99f-4fdb-ad8b-089ac4798bae"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts/{}".format(API_BASE_URL, self.business_uuid, account_uuid)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_ledger_account_response")),
            status=200
        )

        ledger_account = self.freshBooksClient.ledger_accounts.get(self.business_uuid, account_uuid)

        assert str(ledger_account) == "Result(data)"
        assert ledger_account.uuid == account_uuid
        assert ledger_account.name == "Cash"
        assert ledger_account.data["name"] == "Cash"
        assert ledger_account.sub_type == "Cash & Bank"
        assert ledger_account.data["sub_type"] == "Cash & Bank"
        assert ledger_account.data["updated_at"] == "2022-09-22T08:47:04.668685Z"
        assert ledger_account.updated_at == datetime(2022, 9, 22, 8, 47, 4, 668685, tzinfo=timezone.utc)

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert (httpretty.last_request().headers["user-agent"]
                == f"FreshBooks python sdk/{VERSION} client_id some_client")
    
    @httpretty.activate
    def test_get_ledger_account__not_found_error(self):
        account_uuid = "e17f9556-c99f-4fdb-ad8b-089ac4798bae"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts/{}".format(API_BASE_URL, self.business_uuid, account_uuid)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_ledger_account_response__not_found")),
            status=404
        )
        try:
            self.freshBooksClient.ledger_accounts.get(self.business_uuid, account_uuid)
        except FreshBooksError as e:
            assert str(e) == "Request failed with status code 404"
            assert e.status_code == 404
            assert e.error_details == [{
                "reason": "Not found.",
                "metadata": {
                    "message": "Not found.",
                    "field": None
                }
            }]

    @httpretty.activate
    def test_list_ledger_accounts(self):
        account_uuid = "e17f9556-c99f-4fdb-ad8b-089ac4798bae"
        url = "{}/accounting/businesses/{}/ledger_accounts/accounts".format(API_BASE_URL, self.business_uuid)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_ledger_account_response")),
            status=200
        )

        ledger_accounts = self.freshBooksClient.ledger_accounts.list(self.business_uuid)

        assert str(ledger_accounts) == "ListResult(data)"
        assert len(ledger_accounts) == 3
        ledger_account = ledger_accounts[0]
        assert ledger_account.uuid == account_uuid
        assert ledger_account.name == "Cash"
        assert ledger_account.data["name"] == "Cash"
        assert ledger_account.sub_type == "Cash & Bank"
        assert ledger_account.data["sub_type"] == "Cash & Bank"
        assert ledger_account.data["updated_at"] == "2022-09-22T08:47:04.668685Z"
        assert ledger_account.updated_at == datetime(2022, 9, 22, 8, 47, 4, 668685, tzinfo=timezone.utc)

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None
        assert (httpretty.last_request().headers["user-agent"]
                == f"FreshBooks python sdk/{VERSION} client_id some_client")