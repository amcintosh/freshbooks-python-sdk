# Current User

FreshBooks users are uniquely identified by their email across our entire product. One user may act on several
Businesses in different ways, and our Identity model is how we keep track of it. Each unique user has an Identity, and
each Identity has Business Memberships which define the permissions they have.

See [FreshBooks API - Business, Roles, and Identity](https://www.freshbooks.com/api/me_endpoint) and
[FreshBooks API - The Identity Model](https://www.freshbooks.com/api/identity_model).

The current user can be accessed by:

```python
>>> current_user = freshBooksClient.current_user()
>>> current_user.email
<some email>

>>> current_user.business_memberships
<list of businesses>
```
