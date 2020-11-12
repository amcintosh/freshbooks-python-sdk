# FreshBooks Python SDK

The FreshBooks Python SDK allows you to more easily utilize the FreshBooks API.

## Installation

TBD when in pypi.

## Usage

### Configuring the API client

You can create an instance of the API client in one of two ways:

- By providing your application's OAuth2 `client_id` and `client_secret` and following through the auth flow, which when complete will return an access token
- Or if you already have a valid access token, you can instanciate the client directly using that token, however token refresh flows will not function without the application id and secret.

```python
from freshbooks import Client

freshBooksClient = FreshBooksClient(
    client_id=<your application id>,
    client_secret=<your application secret>,
    redirect_uri=<your redirect uri>
)
```

and then proceed with the auth flow (see below).

Or

```python
from freshbooks import Client

freshBooksClient = FreshBooksClient(access_token=<a valid token>)
```

#### Authoization flow

TODO: Not yet written.

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

API calls with returning a list of resources return a `ListResult` object. The resources in the list can be accessed by index and iterated over. Similarly, the raw dictionary can be accessed via the `data` attribute.

```python
clients = freshBooksClient.clients.list(account_id)

assert clients[0].organization == "FreshBooks"

assert clients.data["clients"][0]["organization"] == "FreshBooks"

for client in clients:
    assert client.organization == "FreshBooks"
    assert client.data["organization"] == "FreshBooks"
```

#### Create and Update

#### Pagination, Filters, and Includes

##### Pagination

Pagination results are included in `list` responses in the `pages` attribute:

```python
>>> clients.pages
PageResult(page=1, pages=1, per_page=30, total=6)

>>> clients.pages.total
6
```

To make change a paginated call, first build a `Pagination` object that can be passed into the `list` method.

```python
>>> from freshbooks import Pagination

>>> p = Pagination(2, 4)
>>> p
Pagination(page=2, per_page=4)

>>> clients = freshBooksClient.clients.list(account_id, pagination=p)
>>> clients.pages
PageResult(page=2, pages=3, per_page=4, total=9)
```

`Pagination` has methods `page` and `per_page` to return or set the values. When setting the values the calls can be chained.

```python
>>> p = Pagination(1, 3)
>>> p
Pagination(page=2, per_page=4)

>>> pagination.page()
1

>>> p.page(2).per_page(4)
>>> p
Pagination(page=2, per_page=4)
```

##### Filters

##### Includes

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
