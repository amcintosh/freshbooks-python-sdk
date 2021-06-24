class Builder:

    def build(self, resource_name: str) -> str:  # pragma: no cover
        """Builds the query string parameters from the Builder.

        Args:
            resource_name: The type of resource to generate the query string for.
                           Eg. AccountingResource, ProjectsResource

        Returns:
            The built query string
        """
        raise NotImplementedError
