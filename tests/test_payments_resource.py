import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError
from freshbooks.client import API_BASE_URL


PAYMENT_OPTIONS = {
    "gateway_name": "fbpay",
    "has_credit_card": True,
    "has_ach_transfer": False,
    "has_bacs_debit": False,
    "has_sepa_debit": False,
    "has_acss_debit": False,
    "stripe_acss_payment_options": None,
    "has_paypal_smart_checkout": False,
    "allow_partial_payments": False,
    "entity_type": "invoice",
    "entity_id": "2409177",
    "gateway_info": {
        "id": "abcdef",
        "account_id": "210000012",
        "country": "CA",
        "user_publishable_key": None,
        "currencies": [
            "CAD"
        ],
        "bank_transfer_enabled": False,
        "gateway_name": "fbpay",
        "can_process_payments": True
    }
}


class TestPaymentsResources:
    def setup_method(self, method):
        self.account_id = "ACM123"
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_default_invoice_payment_option(self):
        payment_options_response = {
            "payment_options": PAYMENT_OPTIONS
        }
        url = "{}/payments/account/{}/payment_options".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(payment_options_response),
            status=200
        )

        payment_options = self.freshBooksClient.invoice_payment_options.defaults(self.account_id)

        assert str(payment_options) == "Result(payment_options)"
        assert payment_options.gateway_name == "fbpay"
        assert payment_options.data["gateway_name"] == "fbpay"
        assert payment_options.has_credit_card is True
        assert payment_options.has_ach_transfer is False
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_default_invoice_payment_option__validation_error(self):
        payment_options_response = {
            "error_type": "validation",
            "message": "A validation error occurred.",
            "errors": [
                {
                    "error_type": "type_error.enum",
                    "message": "value is not a valid enumeration member; permitted: 'invoice', 'invoices', "
                    "'invoice_profile', 'checkout_link', 'payment_method_setup'",
                    "field": "entity_type"
                }
            ]
        }
        url = "{}/payments/account/{}/payment_options".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(payment_options_response),
            status=400
        )

        try:
            self.freshBooksClient.invoice_payment_options.defaults(self.account_id)
        except FreshBooksError as e:
            assert str(e) == ("entity_type: value is not a valid enumeration member; permitted: 'invoice', "
                              "'invoices', 'invoice_profile', 'checkout_link', 'payment_method_setup'")
            assert e.status_code == 400
            assert e.error_code is None

    @httpretty.activate
    def test_get_invoice_payment_option(self):
        invoice_id = 12345
        payment_options_response = {
            "payment_options": PAYMENT_OPTIONS
        }
        url = "{}/payments/account/{}/invoice/{}/payment_options".format(API_BASE_URL, self.account_id, invoice_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(payment_options_response),
            status=200
        )

        payment_options = self.freshBooksClient.invoice_payment_options.get(self.account_id, invoice_id)

        assert str(payment_options) == "Result(payment_options)"
        assert payment_options.gateway_name == "fbpay"
        assert payment_options.data["gateway_name"] == "fbpay"
        assert payment_options.has_credit_card is True
        assert payment_options.has_ach_transfer is False
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_get_invoice_payment_option__not_found(self):
        invoice_id = 12345
        payment_options_response = {
            "error_type": "not_found",
            "message": "Resource not found"
        }
        url = "{}/payments/account/{}/invoice/{}/payment_options".format(API_BASE_URL, self.account_id, invoice_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(payment_options_response),
            status=404
        )

        try:
            self.freshBooksClient.invoice_payment_options.get(self.account_id, invoice_id)
        except FreshBooksError as e:
            assert str(e) == "Resource not found"
            assert e.status_code == 404
            assert e.error_code is None

    @httpretty.activate
    def test_get_invoice_payment_option__bad_response(self):
        invoice_id = 12345
        url = "{}/payments/account/{}/invoice/{}/payment_options".format(API_BASE_URL, self.account_id, invoice_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="stuff",
            status=500
        )

        try:
            self.freshBooksClient.invoice_payment_options.get(self.account_id, invoice_id)
        except FreshBooksError as e:
            assert str(e) == "Failed to parse response"
            assert e.status_code == 500
            assert e.error_code is None

    @httpretty.activate
    def test_create_invoice_payment_option(self):
        invoice_id = 12345
        payment_options_data = {
            "gateway_name": "fbpay",
            "entity_id": invoice_id,
            "entity_type": "invoice",
            "has_credit_card": True
        }
        payment_options_response = {
            "payment_options": PAYMENT_OPTIONS
        }
        url = "{}/payments/account/{}/invoice/{}/payment_options".format(API_BASE_URL, self.account_id, invoice_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(payment_options_response),
            status=200
        )

        payment_options = self.freshBooksClient.invoice_payment_options.create(
            self.account_id, invoice_id, payment_options_data
        )

        assert str(payment_options) == "Result(payment_options)"
        assert payment_options.gateway_name == "fbpay"
        assert payment_options.data["gateway_name"] == "fbpay"
        assert payment_options.has_credit_card is True
        assert payment_options.has_ach_transfer is False
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"
