import json
import httpretty

from freshbooks import Client as FreshBooksClient
from freshbooks.client import API_BASE_URL
from tests import get_fixture


class TestTimetrackingResources:
    def setup_method(self, method):
        self.business_id = 98765
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_get_time_entry(self):
        time_entry_id = 419546
        url = "{}/timetracking/business/{}/time_entries/{}".format(API_BASE_URL, self.business_id, time_entry_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("get_time_entry_response")),
            status=200
        )

        time_entry = self.freshBooksClient.time_entries.get(self.business_id, time_entry_id)

        assert str(time_entry) == "Result(time_entry)"
        assert time_entry.data["duration"] == 3600
        assert time_entry.duration == 3600
        assert time_entry.id == time_entry_id
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_list_time_entries(self):
        time_entry_ids = [419546, 419547]
        url = "{}/timetracking/business/{}/time_entries".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=json.dumps(get_fixture("list_time_entries_response")),
            status=200
        )

        time_entries = self.freshBooksClient.time_entries.list(self.business_id)

        assert str(time_entries) == "ListResult(time_entries)"
        assert len(time_entries) == 2
        assert time_entries.pages.total == 2
        assert time_entries.data["meta"]["total"] == 2
        assert time_entries.data["time_entries"][0]["id"] == time_entry_ids[0]
        for index, time_entry in enumerate(time_entries):
            assert time_entry.id == time_entry_ids[index]
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"

    @httpretty.activate
    def test_create_time_entry(self):
        url = "{}/timetracking/business/{}/time_entries".format(API_BASE_URL, self.business_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("get_time_entry_response")),
            status=200
        )

        payload = {
            "billable": True,
            "duration": 3600,
            "note": "Stuff",
            "started_at": "2020-10-17T05:00:00Z",
            "client_id": 56789,
            "project_id": 654321
        }
        time_entry = self.freshBooksClient.time_entries.create(self.business_id, payload)

        assert str(time_entry) == "Result(time_entry)"
        assert time_entry.id == 419546
        assert time_entry.data["duration"] == 3600
        assert time_entry.duration == 3600
        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert httpretty.last_request().headers["Content-Type"] == "application/json"
