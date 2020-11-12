class Pagination:
    """Builder for making paginated list queries.

    Has two attributes, `page` and `per_page`. When a `Pagination` object is passed
    to a `.list()` call, the call will fetch only the `per_page` number of results and will
    fetch the results offset by `page`.

    ```python
    >>> from freshbooks import Pagination

    >>> p = Pagination(2, 4)
    >>> p
    Pagination(page=2, per_page=4)

    >>> clients = freshBooksClient.clients.list(account_id, pagination=p)
    >>> clients.pages
    PageResult(page=2, pages=3, per_page=4, total=9)
    ```
    """

    # TODO: cap per_page and page
    def __init__(self, page=None, per_page=None):
        self._page = page
        self._per_page = per_page

    def __str__(self):
        return f"Pagination(page={self._page}, per_page={self._per_page})"

    def __repr__(self):
        return f"Pagination(page={self._page}, per_page={self._per_page})"

    def page(self, page=None):
        """Set the page you wish to fetch in a list call, or get the currently set the page.
        When setting, can be chained.

        ```python
        >>> p = Pagination(1, 3)
        >>> p
        Pagination(page=2, per_page=4)

        >>> pagination.page()
        1

        >>> p.page(2).per_page(4)
        >>> p
        Pagination(page=2, per_page=4)
        ```
        """
        if page:
            self._page = page
            return self
        return self._page

    def per_page(self, per_page=None):
        """Set the number of results you wish to fetch in a page of a list call,
        or get the currently set per_page. When setting, can be chained.

        ```python
        >>> p = Pagination(1, 3)
        >>> p
        Pagination(page=1, per_page=3)

        >>> pagination.per_page()
        3

        >>> p.per_page(4).page(2)
        >>> p
        Pagination(page=2, per_page=4)
        ```
        """
        if per_page:
            self._per_page = per_page
            return self
        return self._per_page

    def _build(self):
        query_string = ""
        if self._page:
            query_string = f"&page={self._page}"
        if self._per_page:
            query_string = f"{query_string}&per_page={self._per_page}"
        return query_string
