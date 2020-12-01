from collections import namedtuple


class Result:
    """Result object from API calls with a single resource returned.

    Data in the API can be accessed via attributes.

    Example:
    ```python
    client = freshBooksClient.clients.get(account_id, user_id)
    assert client.organization == "FreshBooks"
    assert client.userid == user_id
    ```

    The json-parsed dictionary can also be directly accessed via the `data` attribute.

    Example:
    ```python
    assert client.data["organization"] == "FreshBooks"
    assert client.data["userid"] == user_id
    ```
    """

    def __init__(self, name, data):
        self.name = name
        self.data = data.get(name, {})

    def __str__(self):
        return "Result({})".format(self.name)

    def __repr__(self):  # pragma: no cover
        return "Result({})".format(self.name)

    def __getattr__(self, field):
        return self.data.get(field)


class ListResult:
    """Result object from API calls with a list of resources returned.

    Data in the API can be accessed via attributes.

    Example:
    ```python
    clients = freshBooksClient.clients.list(account_id)
    assert clients[0].organization == "FreshBooks"
    ```

    The json-parsed dictionary can also be directly accessed via the `data` attribute.

    Example:
    ```python
    assert clients.data["clients"][0]["organization"] == "FreshBooks"
    ```

    The list can also be iterated over to access the individual resources as `Result` obejcts.

    Example:
    ```python
    for client in clients:
        assert client.organization == "FreshBooks"
        assert client.data["organization"] == "FreshBooks"
    ```

    Pagination results are included in the `pages` attribute:
    ```python
    >>> clients.pages
    PageResult(page=1, pages=1, per_page=30, total=6)
    >>> clients.pages.total
    6
    ```

    For including pagination in requests, see `freshbooks.builders.paginator.PaginateBuilder`.
    """

    def __init__(self, name, single_name, data):
        self.name = name
        self.single_name = single_name
        self.data = data
        self.pages = self._constructPages(data)

    def __str__(self):
        return "Result({})".format(self.name)

    def __repr__(self):  # pragma: no cover
        return "Result({})".format(self.name)

    def __len__(self):
        return len(self.data.get(self.name, []))

    def __getitem__(self, index):
        results = self.data.get(self.name, [])
        return Result(self.single_name, {self.single_name: results[index]})

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        results = self.data.get(self.name, [])
        if self.n < len(results):
            result = Result(self.single_name, {self.single_name: results[self.n]})
            self.n += 1
            return result
        else:
            raise StopIteration

    def _constructPages(self, data):
        if data.get("meta"):  # Project-style endpoint
            data = data["meta"]
        page = data["page"]
        pages = data["pages"]
        per_page = data["per_page"]
        total = data["total"]
        PageResult = namedtuple("PageResult", ["page", "pages", "per_page", "total"])
        return PageResult(page, pages, per_page, total)


class Identity(Result):
    """An Identity is a `freshbooks.models.Result` object with additional properties and helper methods
    to make accessing the current user's identity easier.

    Example:
    ```python
    >>> current_user = freshBooksClient.current_user
    >>> current_user.email
    <some email>

    >>> current_user.business_memberships
    <list of businesses>
    ```
    """

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "Identity({}, {})".format(self.identity_id, self.data.get("email"))

    def __repr__(self):  # pragma: no cover
        return "Identity({})".format(self.identity_id)

    @property
    def identity_id(self):
        """The authenticated user's identity_id"""
        return self.data.get("identity_id")

    @property
    def name(self):
        """The authenticated user's name"""
        return "{} {}".format(self.data.get("first_name"), self.data.get("last_name"))

    @property
    def business_memberships(self):
        """The authenticated user's businesses and their role in that business."""
        return self.data.get("business_memberships")
