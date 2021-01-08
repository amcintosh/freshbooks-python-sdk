# FreshBooks Python SDK

[![PyPI](https://img.shields.io/pypi/v/freshbooks-sdk)](https://pypi.org/project/freshbooks-sdk/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/freshbooks-sdk)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/freshbooks/freshbooks-python-sdk/Run%20Tests)](https://github.com/freshbooks/freshbooks-python-sdk/actions?query=workflow%3A%22Run+Tests%22)

The FreshBooks Python SDK allows you to more easily utilize the [FreshBooks API](https://www.freshbooks.com/api).

## Installation

```bash
pip install freshbooks-sdk
```

## Usage

See [https://freshbooks.github.io/freshbooks-python-sdk/](https://freshbooks.github.io/freshbooks-python-sdk/) for module documentation.

### Configuring the API client

You can create an instance of the API client in one of two ways:

- By providing your application's OAuth2 `client_id` and `client_secret` and following through the auth flow, which when complete will return an access token
- Or if you already have a valid access token, you can instantiate the client directly using that token, however token refresh flows will not function without the application id and secret.

```python
from freshbooks import Client

freshBooksClient = Client(
    client_id=<your application id>,
    client_secret=<your application secret>,
    redirect_uri=<your redirect uri>
)
```

and then proceed with the auth flow (see below).

Or

```python
from freshbooks import Client

freshBooksClient = Client(
    client_id=<your application id>,
    access_token=<a valid token>
)
```

#### Authoization flow

_This is a brief summary of the OAuth2 authorization flow and the methods in the FreshBooks API Client
around them. See the [FreshBooks API - Authentication](https://www.freshbooks.com/api/authentication) documentation._

First, instantiate your Client with `client_id`, `client_secret`, and `redirect_uri` as above.

To get an access token, the user must first authorize your application. This can be done by sending
the user to the FreshBooks authorization page. Once the user has click accept there, they will be
redirected to your `redirect_uri` with an access grant code. The authorization URL can be obtained by calling `freshBooksClient.get_auth_request_url()`.

Once the user has been redirected to your `redirect_uri` and you have obtained the access grant code, you can exchange that code for a valid access token.

```python
auth_results = freshBooksClient.get_access_token(access_grant_code)
```

This call both sets the `access_token`, `refresh_token`, and `access_token_expires_at` fields on you Client instance, and returns those values.

```python
>>> auth_results.access_token
<some token>

>>> auth_results.refresh_token
<some refresh token>

>>> auth_results.access_token_expires_at
<datetime object>
```

When the token expires, it can be refreshed with the `refresh_token` value in the Client:

```python
>>> auth_results = freshBooksClient.refresh_access_token()
>>> auth_results.access_token
<a new token>
```

or you can pass the refresh token yourself:

```python
>>> auth_results = freshBooksClient.refresh_access_token(stored_refresh_token)
>>> auth_results.access_token
<a new token>
```

### Current User

FreshBooks users are uniquely identified by their email across our entire product. One user may act on several Businesses in different ways, and our Identity model is how we keep track of it. Each unique user has an Identity, and each Identity has Business Memberships which define the permissions they have.

See [FreshBooks API - Business, Roles, and Identity](https://www.freshbooks.com/api/me_endpoint) and
[FreshBooks API - The Identity Model](https://www.freshbooks.com/api/identity_model).

The current user can be accessed by:

```python
>>> current_user = freshBooksClient.current_user
>>> current_user.email
<some email>

>>> current_user.business_memberships
<list of businesses>
```

### Making API Calls

Each resource in the client has provides calls for `get`, `list`, `create`, `update` and `delete` calls. Please note that some API resources are scoped to a FreshBooks `account_id` while others are scoped to a `business_id`. In general these fall along the lines of accounting resources vs projects/time tracking resources, but that is not precise.

```python
client = freshBooksClient.clients.get(account_id, client_user_id)
project = freshBooksClient.projects.get(business_id, project_id)
```

#### Get and List

API calls with a single resouce return a `Result` object with the returned data accessible via attributes. The raw json-parsed dictionary can also be accessed via the `data` attribute.

```python
client = freshBooksClient.clients.get(account_id, client_user_id)

assert client.organization == "FreshBooks"
assert client.userid == user_id

assert client.data["organization"] == "FreshBooks"
assert client.data["userid"] == user_id
```

`vis_state` returns an Enum. See [FreshBooks API - Active and Deleted Objects](https://www.freshbooks.com/api/active_deleted) for details.

```python
from freshbooks import VisState

assert client.vis_state == VisState.ACTIVE
assert client.vis_state == 0
assert client.data['vis_state'] == VisState.ACTIVE
assert client.data['vis_state'] == 0
```

API calls with returning a list of resources return a `ListResult` object. The resources in the list can be accessed by index and iterated over. Similarly, the raw dictionary can be accessed via the `data` attribute.

```python
clients = freshBooksClient.clients.list(account_id)

assert clients[0].organization == "FreshBooks"

assert clients.data["clients"][0]["organization"] == "FreshBooks"

for client in clients:
    assert client.organization == "FreshBooks"
    assert client.data["organization"] == "FreshBooks"
```

#### Create, Update, and Delete

API calls to create and update take a dictionary of the resource data. A successful call will return a `Result` object as if a `get` call.

Create:

```python
payload = {"email": "john.doe@abcorp.com"}
new_client = FreshBooksClient.clients.create(account_id, payload)

client_id = new_client.userid
```

Update:

```python
payload = {"email": "john.doe@abcorp.ca"}
client = freshBooksClient.clients.update(account_id, client_id, payload)

assert client.email == "john.doe@abcorp.ca"
```

Delete:

```python
client = freshBooksClient.clients.delete(account_id, client_id)

assert client.vis_state == VisState.DELETED
```

#### Error Handling

Calls made to the FreshBooks API with a non-2xx response are wrapped in a `FreshBooksError` exception.
This exception class contains the error message, HTTP response code, FreshBooks-specific error number if one exists, and the HTTP response body.

Example:

```python
from freshbooks import FreshBooksError

try:
    client = freshBooksClient.clients.get(account_id, client_id)
except FreshBooksError as e:
    assert str(e) == "Client not found."
    assert e.status_code == 404
    assert e.error_code == 1012
    assert e.raw_response ==  ("{'response': {'errors': [{'errno': 1012, "
                               "'field': 'userid', 'message': 'Client not found.', "
                               "'object': 'client', 'value': '134'}]}}")
```

Not all resources have full CRUD methods available. For example expense categories have `list` and `get`
calls, but are deletable. If you attempt to call a method that does not exist, the SDK will raise a
`FreshBooksNotImplementedError` exception, but this is not something you will likely have to account
for outside of development.

#### Pagination, Filters, and Includes

`list` calls take a list of builder objects that can be used to paginate, filter, and include
optional data in the response. See [FreshBooks API - Parameters](https://www.freshbooks.com/api/parameters) documentation.

##### Pagination

Pagination results are included in `list` responses in the `pages` attribute:

```python
>>> clients.pages
PageResult(page=1, pages=1, per_page=30, total=6)

>>> clients.pages.total
6
```

To make change a paginated call, first build a `PaginateBuilder` object that can be passed into the `list` method.

```python
>>> from freshbooks import PaginateBuilder

>>> paginator = PaginateBuilder(2, 4)
>>> paginator
PaginateBuilder(page=2, per_page=4)

>>> clients = freshBooksClient.clients.list(account_id, builders=[paginator])
>>> clients.pages
PageResult(page=2, pages=3, per_page=4, total=9)
```

`PaginateBuilder` has methods `page` and `per_page` to return or set the values. When setting the values the calls can be chained.

```python
>>> paginator = PaginateBuilder(1, 3)
>>> paginator
PaginateBuilder(page=1, per_page=3)

>>> paginator.page()
1

>>> paginator.page(2).per_page(4)
>>> paginator
PaginateBuilder(page=2, per_page=4)
```

##### Filters

To filter which results are return by `list` method calls, construct a `FilterBuilder` and pass that
in the list of builders to the `list` method.

```python
>>> from freshbooks import FilterBuilder

>>> filter = FilterBuilder()
>>> filter.equals("userid", 123)

>>> clients = freshBooksClient.clients.list(account_id, builders=[filter])
```

Filters can be builts with the methods: `equals`, `in_list`, `like`, `between`, and `boolean`,
which can be chained together.

```python
>>> f = FilterBuilder()
>>> f.like("email_like", "@freshbooks.com")
FilterBuilder(&search[email_like]=@freshbooks.com)

>>> f = FilterBuilder()
>>> f.in_list("clientids", [123, 456]).boolean("active", False)
FilterBuilder(&search[clientids][]=123&search[clientids][]=456&active=False)

>>> f = FilterBuilder()
>>> f.boolean("active", False).in_list("clientids", [123, 456])
FilterBuilder(&active=False&search[clientids][]=123&search[clientids][]=456)

>>> f = FilterBuilder()
>>> f.between("amount", 1, 10)
FilterBuilder(&search[amount_min]=1&search[amount_max]=10)

>>> f = FilterBuilder()
>>> f.between("start_date", date.today())
FilterBuilder(&search[start_date]=2020-11-21)
```

##### Includes

To include additional relationships, sub-resources, or data in a list or get response, a `IncludesBuilder`
can be constructed.

```python
>>> from freshbooks import IncludesBuilder

>>> includes = IncludesBuilder()
>>> includes.include("outstanding_balance")
IncludesBuilder(&include[]=outstanding_balance)
```

Which can then be passed into `list` or `get` calls:

```python
>>> clients = freshBooksClient.clients.list(account_id, builders=[includes])
>>> clients[0].outstanding_balance
[{'amount': {'amount': '100.00', 'code': 'USD'}}]

>>> client = freshBooksClient.clients.get(account_id, client_id, includes=[includes])
>>> client.outstanding_balance
[{'amount': {'amount': '100.00', 'code': 'USD'}}]
```

##### Sorting

## Development

### Testing

To run all tests:

```bash
make test
```

To run a single test with pytest:

```bash
py.test path/to/test/file.py
py.test path/to/test/file.py::TestClass::test_case
```

### Documentations

You can generate the documentation via:

```bash
make generate-docs
```
