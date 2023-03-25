from typing import Optional

from freshbooks.builders import Builder


class SortBuilder(Builder):
    """Builder for including sort by field data in a list request.

    ```python
    >>> from freshbooks import SortBuilder

    >>> sort = SortBuilder()
    >>> sort.ascending("invoice_date")
    SortBuilder(&sort=invoice_date_asc)
    ```
    """

    def __init__(self) -> None:
        self._sort: Optional[str] = None
        self._ascending = True

    def __str__(self) -> str:
        query_string = self.build()
        return f"SortBuilder({query_string})"

    def __repr__(self) -> str:  # pragma: no cover
        query_string = self.build()
        return f"SortBuilder({query_string})"

    def asc(self, key: str) -> Builder:
        """Alias for .ascending()"""
        return self.ascending(key)

    def ascending(self, key: str) -> Builder:
        """Add a sort by the field in ascending order.

        Args:
            key: The field for the resource list to be sorted by
        """
        self._sort = key
        self._ascending = True
        return self

    def desc(self, key: str) -> Builder:
        """Alias for .descending()"""
        return self.descending(key)

    def descending(self, key: str) -> Builder:
        """Add a sort by the field in descending order.

        Args:
            key: The field for the resource list to be sorted by
        """
        self._sort = key
        self._ascending = False
        return self

    def build(self, resource_name: Optional[str] = None) -> str:
        """Builds the query string parameter from the SortBuilder.

        Args:
            resource_name:
                The type of resource to generate the query string for. Eg. AccountingResource, ProjectsResource

        Returns:
            The built query string
        """
        if not self._sort:
            return ""

        if not resource_name or resource_name in ["AccountingResource", "EventsResource"]:
            return f"&sort={self._sort}_asc" if self._ascending else f"&sort={self._sort}_desc"
        return f"&sort={self._sort}" if self._ascending else f"&sort=-{self._sort}"
