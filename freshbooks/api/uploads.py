from io import BufferedReader
from types import SimpleNamespace
from typing import Optional

import requests
from freshbooks.api.resource import HttpVerbs, Resource
from freshbooks.errors import FreshBooksError
from freshbooks.models import Result


class UploadsResource(Resource):
    """Handles resources under the `/uploads` endpoints."""

    def __init__(self, client_config: SimpleNamespace, upload_path: str, single_name: str):
        super().__init__(client_config)
        self.upload_path = upload_path
        self.single_name = single_name

    def _get_url(self, account_id: Optional[str] = None, jwt: Optional[str] = None) -> str:
        if account_id:
            return "{}/uploads/account/{}/{}".format(self.base_url, account_id, self.upload_path)
        return "{}/uploads/{}/{}".format(self.base_url, self.upload_path, jwt)

    def get(self, jwt: str) -> requests.Response:
        """Get an uploaded file. This returns a requests.Response object to provide flexibility
        in handling the data.

        [Requests Binary Response](https://docs.python-requests.org/en/master/user/quickstart/#binary-response-content)

        Args:
            jwt: JWT provided by FreshBooks when the file was uploaded.
        Returns:
            requests.Response: The requests Response object.
        Raises:
            FreshBooksError: If the call is not successful.
        """
        url = self._get_url(jwt=jwt)

        response = self._send_request(url, HttpVerbs.GET)

        status = response.status_code
        if status >= 400:
            try:
                content = response.json()
            except ValueError:
                raise FreshBooksError(status, "Failed to parse response", raw_response=response.text)
            raise FreshBooksError(status, content["error"], raw_response=response.text)

        return response

    def upload(
        self, account_id: str, file_stream: Optional[BufferedReader] = None, file_path: Optional[str] = None
    ) -> Result:
        """Upload a file to FreshBooks' file storage. This returns a Result object with the JWT required to access the file,
        and in the case of an image, a link to the image itself.

        The file to upload can be either a byte stream, or a path to the file itself.

        Eg.

        ```python
        >>> uploaded = freshBooksClient.images.upload(account_id, file_path="/path/to/image.png")
        >>> uploaded = freshBooksClient.images.upload(account_id, file_stream=open("/path/to/image.png", "rb")

        >>> print(uploaded.jwt)
        <some jwt>

        >>> print(uploaded.link)
        https://my.freshbooks.com/service/uploads/images/<some jwt>
        ```

        Args:
            account_id: The alpha-numeric account id
            file_stream: (Optional) Byte stream of the file
            file_path: (Optional) Path to the file
        Returns:
            Result: Result object with the new resource's response data.
        Raises:
            FreshBooksError: If the call is not successful.
        """
        url = self._get_url(account_id=account_id)

        file_content = file_stream
        if file_path and not file_stream:  # pragma: no cover
            file_content = open(file_path, "rb")
        files = {'content': file_content}

        response = self._send_request(url, HttpVerbs.POST, files=files)

        status = response.status_code
        try:
            content = response.json()
        except ValueError:
            raise FreshBooksError(status, "Failed to parse response", raw_response=response.text)

        if status >= 400:
            raise FreshBooksError(status, content["error"], raw_response=response.text)

        if self.single_name not in content:  # pragma: no cover
            raise FreshBooksError(status, "Returned an unexpected response", raw_response=response.text)

        if content.get("link"):
            content[self.single_name]["link"] = content["link"]

        return Result(self.single_name, content)
