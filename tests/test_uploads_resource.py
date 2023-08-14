import json

import httpretty
from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError
from freshbooks.client import API_BASE_URL

from tests import get_fixture


class TestUploadsResources:
    def setup_method(self, method):
        self.account_id = "ACM123"
        self.freshBooksClient = FreshBooksClient(client_id="some_client", access_token="some_token")

    @httpretty.activate
    def test_get_image(self):
        some_jwt = "some_jwt"
        url = "{}/uploads/images/{}".format(API_BASE_URL, some_jwt)
        httpretty.register_uri(httpretty.GET, url, status=200)

        response = self.freshBooksClient.images.get(some_jwt)

        assert response.status_code == 200
        assert type(response.content) is bytes

        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_get_image__not_found(self):
        some_jwt = "some_jwt"
        url = "{}/uploads/images/{}".format(API_BASE_URL, some_jwt)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body='{"error": "File not found"}',
            status=404
        )

        try:
            self.freshBooksClient.images.get(some_jwt)
        except FreshBooksError as e:
            assert str(e) == "File not found"
            assert e.status_code == 404
            assert e.error_code is None

    @httpretty.activate
    def test_get_image__bad_response(self):
        some_jwt = "some_jwt"
        url = "{}/uploads/images/{}".format(API_BASE_URL, some_jwt)
        httpretty.register_uri(
            httpretty.GET,
            url,
            body="blah",
            status=400
        )

        try:
            self.freshBooksClient.images.get(some_jwt)
        except FreshBooksError as e:
            assert str(e) == "Failed to parse response"
            assert e.status_code == 400
            assert e.error_code is None

    @httpretty.activate
    def test_get_attachment(self):
        some_jwt = "some_jwt"
        url = "{}/uploads/attachments/{}".format(API_BASE_URL, some_jwt)
        httpretty.register_uri(httpretty.GET, url, status=200)

        response = self.freshBooksClient.attachments.get(some_jwt)

        assert response.status_code == 200
        assert type(response.content) is bytes

        assert httpretty.last_request().headers["Content-Type"] is None

    @httpretty.activate
    def test_upload_image(self):
        url = "{}/uploads/account/{}/images".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("upload_image_response")),
            status=200
        )

        image = self.freshBooksClient.images.upload(self.account_id, file_stream=None)

        assert str(image) == "Result(image)"
        assert image.jwt == "some_jwt"
        assert image.public_id == "some_jwt"
        assert image.filename == "upload-12345"
        assert image.media_type == "image/jpeg"
        assert image.uuid == "abc-123-aaa"
        assert image.link == "https://my.freshbooks.com/service/uploads/images/some_jwt"

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert "multipart/form-data" in httpretty.last_request().headers["Content-Type"]

    @httpretty.activate
    def test_upload_image__bad_response(self):
        url = "{}/uploads/account/{}/images".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(httpretty.POST, url, body="", status=500)

        try:
            self.freshBooksClient.images.upload(self.account_id, file_stream=None)
        except FreshBooksError as e:
            assert str(e) == "Failed to parse response"
            assert e.status_code == 500
            assert e.error_code is None

    @httpretty.activate
    def test_upload_image__bad_request(self):
        url = "{}/uploads/account/{}/images".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(httpretty.POST, url, body='{"error": "Method not allowed"}', status=422)

        try:
            self.freshBooksClient.images.upload(self.account_id, file_stream=None)
        except FreshBooksError as e:
            assert str(e) == "Method not allowed"
            assert e.status_code == 422
            assert e.error_code is None

    @httpretty.activate
    def test_upload_attachment(self):
        url = "{}/uploads/account/{}/attachments".format(API_BASE_URL, self.account_id)
        httpretty.register_uri(
            httpretty.POST,
            url,
            body=json.dumps(get_fixture("upload_attachment_response")),
            status=200
        )

        attachment = self.freshBooksClient.attachments.upload(self.account_id, file_stream=None)

        assert str(attachment) == "Result(attachment)"
        assert attachment.jwt == "some_jwt"
        assert attachment.public_id == "some_jwt"
        assert attachment.filename == "upload-12345"
        assert attachment.media_type == "image/jpeg"
        assert attachment.uuid == "abc-123-aaa"
        assert attachment.data.get("link") is None

        assert httpretty.last_request().headers["Authorization"] == "Bearer some_token"
        assert "multipart/form-data" in httpretty.last_request().headers["Content-Type"]
