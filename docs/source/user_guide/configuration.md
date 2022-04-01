
# Configuring The API Client

You can create an instance of the API client in one of two ways:

- By providing your application's OAuth2 `client_id` and `client_secret` and following through the auth flow, which when
complete will return an access token
- Or if you already have a valid access token, you can instantiate the client directly using that token, however token
refresh flows will not function without the application id and secret.

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
