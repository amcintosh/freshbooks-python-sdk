# Making API Calls

Each resource in the client provides calls for `get`, `list`, `create`, `update` and `delete` calls. Please note that
some API resources are scoped to a FreshBooks `account_id` while others are scoped to a `business_id`. In general these
fall along the lines of accounting resources vs projects/time tracking resources, but that is not precise.

```python
client = freshBooksClient.clients.get(account_id, client_user_id)
project = freshBooksClient.projects.get(business_id, project_id)
```

## Get and List

API calls which return a single resource return a `Result` object with the returned data accessible via attributes.
The raw json-parsed dictionary can also be accessed via the `data` attribute.

```python
client = freshBooksClient.clients.get(account_id, client_user_id)

assert client.organization == "FreshBooks"
assert client.userid == client_user_id

assert client.data["organization"] == "FreshBooks"
assert client.data["userid"] == client_user_id
```

`vis_state` returns an Enum. See [FreshBooks API - Active and Deleted Objects](https://www.freshbooks.com/api/active_deleted)
for details.

```python
from freshbooks import VisState

assert client.vis_state == VisState.ACTIVE
assert client.vis_state == 0
assert client.data['vis_state'] == VisState.ACTIVE
assert client.data['vis_state'] == 0
```

API calls which return a list of resources return a `ListResult` object. The resources in the list can be accessed by
index and iterated over. Similarly, the raw dictionary can be accessed via the `data` attribute.

```python
clients = freshBooksClient.clients.list(account_id)

assert clients[0].organization == "FreshBooks"

assert clients.data["clients"][0]["organization"] == "FreshBooks"

for client in clients:
    assert client.organization == "FreshBooks"
    assert client.data["organization"] == "FreshBooks"
```

## Create, Update, and Delete

API calls to create and update take a dictionary of the resource data. A successful call will return a `Result` object
as if a `get` call.

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

## Error Handling

Calls made to the FreshBooks API with a non-2xx response are wrapped in a `FreshBooksError` exception.
This exception class contains the error message, HTTP response code, FreshBooks-specific error number if one exists,
and the HTTP response body.

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
calls, but are not deletable. If you attempt to call a method that does not exist, the SDK will raise a
`FreshBooksNotImplementedError` exception, but this is not something you will likely have to account
for outside of development.

## Pagination, Filters, and Includes

`list` calls take a list of builder objects that can be used to paginate, filter, and include
optional data in the response. See [FreshBooks API - Parameters](https://www.freshbooks.com/api/parameters) documentation.

### Pagination

Pagination results are included in `list` responses in the `pages` attribute:

```python
>>> clients = freshBooksClient.clients.list(account_id)
>>> clients.pages
PageResult(page=1, pages=1, per_page=30, total=6)

>>> clients.pages.total
6
```

To make a paginated call, first create a `PaginateBuilder` object that can be passed into the `list` method.

```python
>>> from freshbooks import PaginateBuilder

>>> paginator = PaginateBuilder(2, 4)
>>> paginator
PaginateBuilder(page=2, per_page=4)

>>> clients = freshBooksClient.clients.list(account_id, builders=[paginator])
>>> clients.pages
PageResult(page=2, pages=3, per_page=4, total=9)
```

`PaginateBuilder` has methods `page` and `per_page` to return or set the values. When setting the values the calls
can be chained.

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

ListResults can be combined, allowing your to use pagination to get all the results of a resource.

```python
paginator = PaginateBuilder(1, 100)
clients = freshBooksClient.clients.list(self.account_id, builders=[paginator])
while clients.pages.page < clients.pages.pages:
    paginator.page(clients.pages.page + 1)
    new_clients = freshBooksClient.clients.list(self.account_id, builders=[paginator])
    clients = clients + new_clients
```

### Filters

To filter which results are return by `list` method calls, construct a `FilterBuilder` and pass that
in the list of builders to the `list` method.

```python
>>> from freshbooks import FilterBuilder

>>> filter = FilterBuilder()
>>> filter.equals("userid", 123)

>>> clients = freshBooksClient.clients.list(account_id, builders=[filter])
```

Filters can be built with the methods: `equals`, `in_list`, `like`, `between`, and `boolean`,
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

### Includes

To include additional relationships, sub-resources, or data in a response an `IncludesBuilder`
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

>>> client = freshBooksClient.clients.get(account_id, client_id, includes=includes)
>>> client.outstanding_balance
[{'amount': {'amount': '100.00', 'code': 'USD'}}]
```

Includes can also be passed into `create` and `update` calls to include the data in the response of the updated resource:

```python
>>> payload = {"email": "john.doe@abcorp.com"}
>>> new_client = FreshBooksClient.clients.create(account_id, payload, includes=includes)
>>> new_client.outstanding_balance
[]  # New client has no balance
```

## Dates and Times

For historical reasons, some resources in the FreshBooks API (mostly accounting-releated) return date/times in
"US/Eastern" timezone. Some effort is taken to return `datetime` objects as zone-aware and normalized to UTC. In these
cases, the raw response string will differ from the attribute. For example:

```python
from datetime import datetime, timezone

assert client.data["updated"] == "2021-04-16 10:31:59"  # Zone-naive string in "US/Eastern"
assert client.updated.isoformat() == '2021-04-16T14:31:59+00:00'  # Zone-aware datetime in UTC
assert client.updated == datetime(year=2021, month=4, day=16, hour=14, minute=31, second=59, tzinfo=timezone.utc)
```
