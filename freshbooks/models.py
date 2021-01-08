from collections import namedtuple
from enum import IntEnum
from typing import Any, Optional, Union


class VisState(IntEnum):
    """Enum of FreshBooks entity vis_status values"""
    ACTIVE = 0
    DELETED = 1
    ARCHIVED = 2


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

    def __init__(self, name: Optional[str], data: dict):
        self._name = name
        self.data = data.get(name, {})

    def __str__(self) -> str:
        return "Result({})".format(self._name)

    def __repr__(self) -> str:  # pragma: no cover
        return "Result({})".format(self._name)

    def __getattr__(self, field: str) -> Any:
        field_data = self.data.get(field)
        if isinstance(field_data, dict):
            return Result(field, {field: field_data})
        if isinstance(field_data, list):
            return ListResult(field, field, {field: field_data}, include_pages=False)
        return field_data

    @property
    def vis_state(self) -> Union[VisState, None]:
        if self.data.get('vis_state') in list(VisState):
            return VisState(self.data['vis_state'])
        return None


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

    def __init__(self, name: str, single_name: str, data: dict, include_pages: bool = True):
        self._name = name
        self._single_name = single_name
        self.data = data
        if include_pages:
            self.pages = self._constructPages(data)

    def __str__(self) -> str:
        return "ListResult({})".format(self._name)

    def __repr__(self) -> str:  # pragma: no cover
        return "ListResult({})".format(self._name)

    def __len__(self) -> int:
        return len(self.data.get(self._name, []))

    def __getitem__(self, index: int) -> Result:
        results = self.data.get(self._name, [])
        return Result(self._single_name, {self._single_name: results[index]})

    def __iter__(self) -> Any:
        self.n = 0
        return self

    def __next__(self) -> Result:
        results = self.data.get(self._name, [])
        if self.n < len(results):
            result = Result(self._single_name, {self._single_name: results[self.n]})
            self.n += 1
            return result
        else:
            raise StopIteration

    def _constructPages(self, data: dict) -> Any:
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

    def __init__(self, data: dict):
        self.data = data

    def __str__(self) -> str:
        return "Identity({}, {})".format(self.identity_id, self.data.get("email"))

    def __repr__(self) -> str:  # pragma: no cover
        return "Identity({})".format(self.identity_id)

    @property
    def identity_id(self) -> int:
        """The authenticated user's identity_id"""
        return self.data.get("identity_id")  # type: ignore

    @property
    def full_name(self) -> str:
        """The authenticated user's name"""
        return "{} {}".format(self.data.get("first_name"), self.data.get("last_name"))

    @property
    def business_memberships(self) -> Any:
        """The authenticated user's businesses and their role in that business."""
        return self.data.get("business_memberships")
