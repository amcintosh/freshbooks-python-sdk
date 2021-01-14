from typing import List, Optional

from freshbooks.builders import Builder


class IncludesBuilder(Builder):
    """Builder for including relationships, sub-resources, or additional data in the response.

    ```python
    >>> from freshbooks import IncludesBuilder

    >>> includes = IncludesBuilder()
    >>> includes.include("late_reminders")
    IncludesBuilder(&include[]=late_reminders)
    """

    def __init__(self) -> None:
        self._includes: List[str] = []

    def __str__(self) -> str:
        query_string = self.build()
        return f"IncludesBuilder({query_string})"

    def __repr__(self) -> str:  # pragma: no cover
        query_string = self.build()
        return f"IncludesBuilder({query_string})"

    def include(self, key: str) -> Builder:
        """Add an include key to the builder.

        Example:
        `includes.include("late_reminders")` will yield the filter `&include[]=late_reminders`

        Args:
            key: The key for the resource or data to include

        Returns:
            The IncludesBuilder instance
        """
        self._includes.append(key)
        return self

    def build(self, resource_name: Optional[str] = None) -> str:
        """Builds the query string parameters from the IncludesBuilder.

        Returns:
            The built query string
        """
        query_string = ""
        for key in self._includes:
            if not resource_name or resource_name in ["AccountingResource", "EventsResource"]:
                query_string = f"{query_string}&include[]={key}"
            else:
                query_string = f"{query_string}&{key}=true"
        return query_string
