
# Authorization Flow

_This is a brief summary of the OAuth2 authorization flow and the methods in the FreshBooks API Client
around them. See the [FreshBooks API - Authentication](https://www.freshbooks.com/api/authentication) documentation._

First, instantiate your Client with `client_id`, `client_secret`, and `redirect_uri` as above.

To get an access token, the user must first authorize your application. This can be done by sending the user to
the FreshBooks authorization page. Once the user has clicked accept there, they will be redirected to your
`redirect_uri` with an access grant code. The authorization URL can be obtained by calling
`freshBooksClient.get_auth_request_url()`. This method also accepts a list of scopes that you wish the user to
authorize your application for.

```python
auth_url = freshBooksClient.get_auth_request_url(['user:profile:read', 'user:clients:read'])
```

Once the user has been redirected to your `redirect_uri` and you have obtained the access grant code, you can exchange
that code for a valid access token.

```python
auth_results = freshBooksClient.get_access_token(access_grant_code)
```

This call both sets the `access_token`, `refresh_token`, and `access_token_expires_at` fields on you Client instance,
and returns those values.

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
