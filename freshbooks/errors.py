class FreshBooksError(Exception):
    """Exception thrown when FreshBooks returns a non-200 response.

    Example:
    ```python
    try:
        client = freshBooksClient.clients.get(self.account_id, client_id)
    except FreshBooksError as e:
        assert str(e) == "Client not found."
        assert e.status_code == 404
        assert e.error_code == 1012
    ```

    Attributes:
        message: Error message
        status_code: HTTP status code from the server.
        error_code: (Optional) FreshBooks specific error code.
        raw_response: Content response from the server.
    """

    def __init__(self, status_code, message, raw_response=None, error_code=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.raw_response = raw_response


class FailedRequest(Exception):
    """Exception thrown when FreshBooks returns a response, but it is not json parsable.

    Attributes:
        message: Error message.
        status_code: HTTP status code from the server.
        raw_response: Content response from the server.
    """

    def __init__(self, status_code, message, raw_response=None):
        self.status_code = status_code
        self.raw_response = raw_response
        super().__init__("{}: '{}'".format(message, raw_response))
