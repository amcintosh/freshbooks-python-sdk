import os
from freshbooks.api.accounting import AccountingResource
from freshbooks.api.projects import ProjectsResource

API_BASE_URL = "https://api.freshbooks.com"
API_TOKEN_URL = "auth/oauth/token"
AUTH_BASE_URL = "https://my.freshbooks.com"
AUTH_URL = "/service/auth/oauth/authorize"


class Client:
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None,
                 access_token=None, refresh_token=None):
        """
        Create a new API client instance for the given `client_id` and `client_secret`.
        This will allow you to follow the authentication flow to get an `access_token`.

        Alternatively, you can provide an `access_token` directly, in which case then you don't need
        to specify a `client_id` (though the token cannot be refreshed in this case).

        TODO: Rate limits, change timeout

        Args:
            client_id: The FreshBooks application client id
            client_secret: The FreshBooks application client secret
            redirect_uri: Where the user should be redirected to after authentication
            access_token: An already authenticated access token to use
            refresh_token: An already authenticated refresh token to use

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

    def __str__(self):  # pragma: no cover
        return "FreshBooks Client: {}".format(self.client_id or "No client_id")

    @property
    def clients(self):
        """FreshBooks clients resource with calls to get, list.
        """
        return AccountingResource(self.base_url, self.access_token, "users/clients", "client", "clients")

    @property
    def projects(self):
        """FreshBooks clients resource with calls to get.
        """
        return ProjectsResource(self.base_url, self.access_token, "projects", "project")
