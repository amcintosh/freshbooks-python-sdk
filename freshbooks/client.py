import os
from types import SimpleNamespace
from freshbooks.api.accounting import AccountingResource
from freshbooks.api.projects import ProjectsResource

API_BASE_URL = "https://api.freshbooks.com"
API_TOKEN_URL = "auth/oauth/token"
AUTH_BASE_URL = "https://my.freshbooks.com"
AUTH_URL = "/service/auth/oauth/authorize"

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as f:
    VERSION = f.readlines()[0].strip()


class Client:
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None,
                 access_token=None, refresh_token=None, user_agent=None):
        """
        Create a new API client instance for the given `client_id` and `client_secret`.
        This will allow you to follow the authentication flow to get an `access_token`.

        Alternatively, you can provide an `access_token` directly, in which case then you don't need
        to specify a `client_id` (though the token cannot be refreshed in this case).

        TODO: Rate limits, change timeout, retries
        TODO: sub-objects
        TODO: sorting
        TODO: type hints

        Args:
            client_id: The FreshBooks application client id
            client_secret: The FreshBooks application client secret
            redirect_uri: Where the user should be redirected to after authentication
            access_token: An already authenticated access token to use
            refresh_token: An already authenticated refresh token to use
            user_agent: A user-agent string to override the default

        Returns:
            The Client instance
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token

        self.base_url = os.getenv("FRESHBOOKS_API_URL", API_BASE_URL)
        self.authorization_url = "{}{}".format(os.getenv("FRESHBOOKS_AUTH_URL", AUTH_BASE_URL), AUTH_URL)

        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"FreshBooks python sdk/{VERSION}"

    def __str__(self):  # pragma: no cover
        return "FreshBooks Client: {}".format(self.client_id or "No client_id")

    def __repr__(self):  # pragma: no cover
        return "FreshBooks Client: {}".format(self.client_id or "No client_id")

    def _client_resource_config(self):
        return SimpleNamespace(
            access_token=self.access_token,
            base_url=self.base_url,
            user_agent=self.user_agent
        )

    @property
    def clients(self):
        """FreshBooks clients resource with calls to get, list, create, update."""
        return AccountingResource(self._client_resource_config(), "users/clients", "client", "clients")

    @property
    def projects(self):
        """FreshBooks projects resource with calls to get, list."""
        return ProjectsResource(self._client_resource_config(), "projects", "project")
