from datetime import datetime, timedelta
import os
from types import SimpleNamespace
import requests
from requests.models import urlencode
from freshbooks.api.accounting import AccountingResource
from freshbooks.api.auth import AuthResource
from freshbooks.api.projects import ProjectsResource
from freshbooks.errors import FreshBooksError

API_BASE_URL = "https://api.freshbooks.com"
API_TOKEN_URL = "auth/oauth/token"
AUTH_BASE_URL = "https://auth.freshbooks.com"
AUTH_URL = "/service/auth/oauth/authorize"
DEFAULT_TIMEOUT = 30

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as f:
    VERSION = f.readlines()[0].strip()


class Client:
    def __init__(self, client_id, client_secret=None, redirect_uri=None,
                 access_token=None, refresh_token=None, user_agent=None):
        """
        Create a new API client instance for the given `client_id` and `client_secret`.
        This will allow you to follow the authentication flow to get an `access_token`.

        Alternatively, you can provide an `access_token` directly, in which case then you don't need
        to specify a `client_secret` (though the token cannot be refreshed in this case).

        TODO: Rate limits, change timeout, retries
        TODO: identity: get business_id from account and vice
        TODO: identity: get businesses by role
        TODO: includes, sort
        TODO: sub-objects
        TODO: sorting
        TODO: type hints
        TODO: revoke token

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
        self.access_token_expires_at = None

        self.base_url = os.getenv("FRESHBOOKS_API_URL", API_BASE_URL)
        self.authorization_url = "{}{}".format(os.getenv("FRESHBOOKS_AUTH_URL", AUTH_BASE_URL), AUTH_URL)
        self.token_url = "{}{}".format(os.getenv("FRESHBOOKS_AUTH_URL", AUTH_BASE_URL), AUTH_URL)

        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"FreshBooks python sdk/{VERSION} client_id {self.client_id}"

    def __str__(self):  # pragma: no cover
        return f"FreshBooks Client: {self.client_id}"

    def __repr__(self):  # pragma: no cover
        return f"FreshBooks Client: {self.client_id}"

    def _client_resource_config(self):
        return SimpleNamespace(
            access_token=self.access_token,
            base_url=self.base_url,
            user_agent=self.user_agent
        )

    def get_auth_request_url(self, scopes=None):
        """Returns the url that a client needs to request an oauth grant from the server.

        To get an oauth access token, send your user to this URL. The user will be prompted to
        log in to FreshBooks, after which they will be redirected to the `redirect_uri` set on
        the client with the access grant as a parameter. That grant can then be used to fetch an
        access token by calling `get_access_token`.

        Note: The `redirect_uri` must be one of the URLs your application is registered for.

        If scopes are not specified, then the access token will be given the default scopes your
        application is registered for.

        Args:
            scopes: List of scopes if your want an access token with only a subset of your registered scopes

        Returns:
            The URL for the authorization request
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        if scopes:
            params["scope"] = " ".join(scopes)
        formatted_params = "".join(urlencode(params))
        return f"{self.authorization_url}?{formatted_params}"

    def _authorize_call(self, grant_type, code_type, code):
        """Shared logic for making access_token and refresh_token calls"""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": grant_type,
            "redirect_uri": self.redirect_uri,
            code_type: code
        }
        response = requests.post(f"{self.base_url}/{API_TOKEN_URL}", payload, timeout=DEFAULT_TIMEOUT)
        content = response.json()
        try:
            self.access_token = content["access_token"]
            self.refresh_token = content["refresh_token"]
            created_at = datetime.fromtimestamp(content["created_at"])
            expires_in = timedelta(seconds=content["expires_in"])
            self.access_token_expires_at = created_at + expires_in
        except KeyError:
            raise FreshBooksError(response.status_code, "Failed to fetch access_token", raw_response=response.text)
        return SimpleNamespace(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            access_token_expires_at=self.access_token_expires_at
        )

    def get_access_token(self, code):
        """Makes a call to the FreshBooks token URL to get an access_token.

        This requires the access_grant code obtained after the user is redirected by the authorization
        step. See `freshbooks.client.Client.get_auth_request_url`.

        This call sets the `access_token`, `refresh_token`, and `access_token_expires_at` attributes
        on the Client instance and also returns those values in an object.

        Args:
            code: access_grant code from the authorization redirect

        Returns:
            Simplre namespace containing `access_token`, `refresh_token`, and `access_token_expires_at`
        """
        return self._authorize_call("authorization_code", "code", code)

    def refresh_access_token(self, refresh_token=None):
        """Makes a call to the FreshBooks token URL to refresh an access_token.

        If `refresh_token` is provided, it will call to refresh it, otherwise it will use the
        `refresh_token` on the Client instance.

        This call sets the `access_token`, `refresh_token`, and `access_token_expires_at` attributes
        on the Client instance to the new values from the refresh call, and also returns those values
        in an object.

        Args:
            refresh_token: (Optional) refresh_token from initial `get_access_token` call

        Returns:
            Simplre namespace containing `access_token`, `refresh_token`, and `access_token_expires_at`
        """
        refresh_token = refresh_token or self.refresh_token
        return self._authorize_call("refresh_token", "refresh_token", refresh_token)

    @property
    def current_user(self):
        """The identity details of the currently authenticated user.

        See https://www.freshbooks.com/api/me_endpoint
        """
        return AuthResource(self._client_resource_config()).me_endpoint()

    @property
    def clients(self):
        """FreshBooks clients resource with calls to get, list, create, update, delete"""
        return AccountingResource(self._client_resource_config(), "users/clients", "client", "clients")

    @property
    def expenses(self):
        """FreshBooks expenses resource with calls to get, list, create, update, delete"""
        return AccountingResource(self._client_resource_config(), "expenses/expenses", "expense", "expenses")

    @property
    def invoices(self):
        """FreshBooks invoices resource with calls to get, list, create, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "invoices/invoices", "invoice", "invoices", delete_via_update=False
        )

    @property
    def staffs(self):
        """FreshBooks staff resource with calls to get, list, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "users/staffs", "staff", "staffs", missing_endpoints=["create"]
        )

    @property
    def taxes(self):
        """FreshBooks taxes resource with calls to get, list, create, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "taxes/taxes", "tax", "taxes", delete_via_update=False
        )

    @property
    def projects(self):
        """FreshBooks projects resource with calls to get, list, create, update, delete"""
        return ProjectsResource(self._client_resource_config(), "projects", "project")
