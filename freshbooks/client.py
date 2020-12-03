import os
from datetime import datetime, timedelta
import logging
from types import SimpleNamespace
from typing import Optional, List

import requests
from requests.models import urlencode  # type: ignore

from freshbooks.api.accounting import AccountingResource
from freshbooks.api.auth import AuthResource
from freshbooks.api.projects import ProjectsResource
from freshbooks.api.resource import Resource
from freshbooks.api.timetracking import TimetrackingResource
from freshbooks.errors import FreshBooksError, FreshBooksClientConfigError
from freshbooks.models import Identity

API_BASE_URL = "https://api.freshbooks.com"
API_TOKEN_URL = "auth/oauth/token"
AUTH_BASE_URL = "https://auth.freshbooks.com"
AUTH_URL = "/service/auth/oauth/authorize"
DEFAULT_TIMEOUT = 30

logging.getLogger('freshbooks').addHandler(logging.NullHandler())

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as f:
    VERSION = f.readlines()[0].strip()


class Client:
    def __init__(self, client_id: str, client_secret: Optional[str] = None, redirect_uri: Optional[str] = None,
                 access_token: Optional[str] = None, refresh_token: Optional[str] = None,
                 user_agent: Optional[str] = None, auto_retry: bool = True):
        """
        Create a new API client instance for the given `client_id` and `client_secret`.
        This will allow you to follow the authentication flow to get an `access_token`.

        Alternatively, you can provide an `access_token` directly, in which case then you don't need
        to specify a `client_secret` (though the token cannot be refreshed in this case).

        Args:
            client_id: The FreshBooks application client id
            client_secret: The FreshBooks application client secret
            redirect_uri: Where the user should be redirected to after authentication
            access_token: An already authenticated access token to use
            refresh_token: An already authenticated refresh token to use
            user_agent: A user-agent string to override the default
            auto_retry: If the SDK should retry failed call up to 3 times. Defaults to True.

        Returns:
            The Client instance
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.access_token_expires_at: Optional[datetime] = None
        self.auto_retry = auto_retry

        self.base_url = os.getenv("FRESHBOOKS_API_URL", API_BASE_URL)
        self.authorization_url = "{}{}".format(os.getenv("FRESHBOOKS_AUTH_URL", AUTH_BASE_URL), AUTH_URL)
        self.token_url = "{}{}".format(os.getenv("FRESHBOOKS_AUTH_URL", AUTH_BASE_URL), AUTH_URL)

        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"FreshBooks python sdk/{VERSION} client_id {self.client_id}"

    def __str__(self) -> str:  # pragma: no cover
        return f"FreshBooks Client: {self.client_id}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"FreshBooks Client: {self.client_id}"

    def _client_resource_config(self) -> SimpleNamespace:
        return SimpleNamespace(
            access_token=self.access_token,
            base_url=self.base_url,
            user_agent=self.user_agent,
            auto_retry=self.auto_retry
        )

    def get_auth_request_url(self, scopes: Optional[List[str]] = None) -> str:
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

    def _authorize_call(self, grant_type: str, code_type: str, code: str) -> SimpleNamespace:
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
            created_at = datetime.utcfromtimestamp(content["created_at"])
            expires_in = timedelta(seconds=content["expires_in"])
            self.access_token_expires_at = created_at + expires_in
        except KeyError:
            raise FreshBooksError(response.status_code, "Failed to fetch access_token", raw_response=response.text)
        return SimpleNamespace(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            access_token_expires_at=self.access_token_expires_at
        )

    def get_access_token(self, code: str) -> SimpleNamespace:
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

    def refresh_access_token(self, refresh_token: Optional[str] = None) -> SimpleNamespace:
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

        Raises:
            FreshBooksClientConfigError: If a refresh token is not set on the client instance and is not provided.
        """
        refresh_token = refresh_token or self.refresh_token
        if not refresh_token:
            raise FreshBooksClientConfigError("refresh_token required")
        return self._authorize_call("refresh_token", "refresh_token", refresh_token)

    # Auth Resources

    @property
    def current_user(self) -> Identity:
        """The identity details of the currently authenticated user.

        See https://www.freshbooks.com/api/me_endpoint
        """
        return AuthResource(self._client_resource_config()).me_endpoint()

    # Accounting Resources

    @property
    def clients(self) -> Resource:
        """FreshBooks clients resource with calls to get, list, create, update, delete"""
        return AccountingResource(self._client_resource_config(), "users/clients", "client", "clients")

    @property
    def credit_notes(self) -> Resource:
        """FreshBooks credit_notes resource with calls to get, list, create, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "credit_notes/credit_notes", "credit_note", "credit_notes"
        )

    @property
    def estimates(self) -> Resource:
        """FreshBooks estimates resource with calls to get, list, create, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "estimates/estimates", "estimate", "estimates", delete_via_update=False
        )

    @property
    def expenses(self) -> Resource:
        """FreshBooks expenses resource with calls to get, list, create, update, delete"""
        return AccountingResource(self._client_resource_config(), "expenses/expenses", "expense", "expenses")

    @property
    def expenses_categories(self) -> Resource:
        """FreshBooks expenses categories resource with calls to get and list"""
        return AccountingResource(
            self._client_resource_config(), "expenses/categories", "category", "categories",
            missing_endpoints=["create", "update", "delete"]
        )

    @property
    def gateways(self) -> Resource:
        """FreshBooks gateways resource with calls to list, delete"""
        return AccountingResource(
            self._client_resource_config(), "systems/gateways", "gateway", "gateways", delete_via_update=False,
            missing_endpoints=["create", "update", "get"]
        )

    @property
    def invoices(self) -> Resource:
        """FreshBooks invoices resource with calls to get, list, create, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "invoices/invoices", "invoice", "invoices", delete_via_update=False
        )

    @property
    def invoice_profiles(self) -> Resource:
        """FreshBooks invoice_profiles resource with calls to get, list, create, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "invoice_profiles/invoice_profiles", "invoice_profile", "invoice_profiles"
        )

    @property
    def items(self) -> Resource:
        """FreshBooks items resource with calls to get, list, create, update, delete"""
        return AccountingResource(self._client_resource_config(), "items/items", "item", "items")

    @property
    def other_income(self) -> Resource:
        """FreshBooks other_incomes resource with calls to get, list, create, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "other_incomes/other_incomes", "other_income", "other_income",
            delete_via_update=False
        )

    @property
    def payments(self) -> Resource:
        """FreshBooks payments resource with calls to get, list, create, update, delete"""
        return AccountingResource(self._client_resource_config(), "payments/payments", "payment", "payments")

    @property
    def staff(self) -> Resource:
        """FreshBooks staff resource with calls to get, list, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "users/staffs", "staff", "staffs", missing_endpoints=["create"]
        )

    @property
    def systems(self) -> Resource:
        """FreshBooks systems resource with calls to get only"""
        return AccountingResource(
            self._client_resource_config(), "systems/systems", "system", "systems",
            missing_endpoints=["create", "update", "delete", "list"]
        )

    @property
    def taxes(self) -> Resource:
        """FreshBooks taxes resource with calls to get, list, create, update, delete"""
        return AccountingResource(
            self._client_resource_config(), "taxes/taxes", "tax", "taxes", delete_via_update=False
        )

    # Project Resources

    @property
    def projects(self) -> Resource:
        """FreshBooks projects resource with calls to get, list, create, update, delete"""
        return ProjectsResource(self._client_resource_config(), "projects", "project")

    # Time tracking Resources

    @property
    def time_entries(self) -> Resource:
        """FreshBooks time_entries resource with calls to get, list, create, update, delete"""
        return TimetrackingResource(self._client_resource_config(), "time_entries", "time_entry")
