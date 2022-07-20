from typing import Optional


class FreshBooksError(Exception):
    """Exception thrown when FreshBooks returns a non-2xx response or when the response
    is missing expected content.

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
        raw_response: Content response from the server.
        error_code: (Optional) FreshBooks specific error code, if available
        error_details: (Optional) Details of the error, if available
    """

    def __init__(self, status_code: int, message: str,
                 raw_response: Optional[str] = None,
                 error_code: Optional[int] = None,
                 error_details: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.error_details = error_details
        self.raw_response = raw_response


class FreshBooksNotImplementedError(Exception):
    """Exception thrown when making a resource call that does not exist.
    Eg.
    ```python
    >>> freshBooksClient.staff.create()
    ```
    """

    def __init__(self, resource_name: str, method_name: str):
        super().__init__(f"The method '{method_name}' does not exist for {resource_name}")


class FreshBooksClientConfigError(Exception):
    """Exception thrown when optional client parameters are not set, but and required."""
    pass
