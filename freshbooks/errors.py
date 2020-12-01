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
        error_code: (Optional) FreshBooks specific error code, if available
        raw_response: Content response from the server.
    """

    def __init__(self, status_code, message, raw_response=None, error_code=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.raw_response = raw_response


class FreshBooksNotImplementedError(Exception):
    """Exception thrown when making a resource call that does not exist.
    Eg.
    ```python
    >>> freshBooksClient.staff.create()
    ```
    """

    def __init__(self, resource_name, method_name):
        super().__init__(f"The method '{method_name}' does not exist for {resource_name}")
