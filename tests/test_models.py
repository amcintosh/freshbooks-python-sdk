from datetime import datetime, timezone
import pytest
from freshbooks.models import ListResult, Result
from tests import get_fixture


class TestListResult:

    def test_adding_list_results(self):
        data_1 = get_fixture("list_clients_response")["response"]["result"]
        client_results_1 = ListResult("clients", "client", data_1)
        assert len(client_results_1) == 3
        assert client_results_1[0].id == 12345
        assert client_results_1.pages.page == 1

        data_2 = get_fixture("list_clients_response")["response"]["result"]
        data_2["page"] = 2
        client_results_2 = ListResult("clients", "client", data_2)
        assert len(client_results_2) == 3
        assert client_results_2[2].id == 12457
        assert client_results_2.pages.page == 2

        full_results = client_results_1 + client_results_2
        assert len(client_results_1) == 3
        assert len(client_results_2) == 3
        assert len(full_results) == 6
        assert full_results[0].id == 12345
        assert full_results[5].id == 12457
        assert full_results.pages.page == 2

    def test_adding_list_results__takes_largest_page(self):
        data_1 = get_fixture("list_clients_response")["response"]["result"]
        data_1["page"] = 3
        client_results_1 = ListResult("clients", "client", data_1)
        assert client_results_1.data["page"] == 3
        assert client_results_1.pages.page == 3

        data_2 = get_fixture("list_clients_response")["response"]["result"]
        data_2["page"] = 1
        client_results_2 = ListResult("clients", "client", data_2)

        full_results = client_results_1 + client_results_2
        assert len(full_results) == 6
        assert full_results[0].id == 12345
        assert full_results[5].id == 12457
        assert full_results.pages.page == 3

    def test_adding_list_results__must_be_list_result(self):
        data = get_fixture("list_clients_response")["response"]["result"]
        client_results = ListResult("clients", "client", data)

        with pytest.raises(TypeError) as error:
            client_results + 1
        assert str(error.value) == "Objects not of same ListResult type"

    def test_adding_list_results__must_share_response_type(self):
        data = get_fixture("list_clients_response")["response"]["result"]
        client_results = ListResult("clients", "client", data)

        data = get_fixture("list_callbacks_response")["response"]["result"]
        callbacks_results = ListResult("callbacks", "callback", data)

        with pytest.raises(TypeError) as error:
            client_results + callbacks_results
        assert str(error.value) == "Objects not of same ListResult type"

    @pytest.mark.parametrize(
        "model_name, field_name, value, expected",
        [
            # "US/Eastern" converted to "UTC"
            ("client", "updated", "2021-06-28 14:05:15", datetime(2021, 6, 28, 18, 5, 15, tzinfo=timezone.utc)),
            ("invoice", "updated", "2021-07-29 16:22:23", datetime(2021, 7, 29, 20, 22, 23, tzinfo=timezone.utc)),
            # "UTC"
            ("bill", "created_at", "2021-08-18 19:23:46",
                datetime(2021, 8, 18, 19, 23, 46, tzinfo=timezone.utc)),
            ("bill", "updated_at", "2021-08-18 19:23:46",
                datetime(2021, 8, 18, 19, 23, 46, tzinfo=timezone.utc)),
            ("client", "signup_date", "2020-10-30 15:25:34",
                datetime(2020, 10, 30, 15, 25, 34, tzinfo=timezone.utc)),
            ("bill_vendor", "created_at", "2021-08-18 17:59:26",
                datetime(2021, 8, 18, 17, 59, 26, tzinfo=timezone.utc)),
            ("bill_vendor", "updated_at", "2021-08-18 17:59:26",
                datetime(2021, 8, 18, 17, 59, 26, tzinfo=timezone.utc)),
            ("tax_defaults", "created_at", "2021-08-18 19:17:05",
                datetime(2021, 8, 18, 19, 17, 5, tzinfo=timezone.utc)),
            ("tax_defaults", "updated_at", "2021-08-18 19:17:05",
                datetime(2021, 8, 18, 19, 17, 5, tzinfo=timezone.utc)),
        ]
    )
    def test_accounting_datetimes_utc(self, model_name, field_name, value, expected):
        result = Result(model_name, {model_name: {field_name: value}})

        assert getattr(result, field_name) == expected, f"{model_name}.{field_name} should equal {expected}"
