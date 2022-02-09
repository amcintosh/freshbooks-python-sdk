# This is an example where we run through the OAuth flow,
# select a business, and display a client from that business.

from types import SimpleNamespace
from freshbooks import Client as FreshBooksClient

fb_client_id = "<your client id>"
secret = "<your client secret>"
redirect_uri = "<your redirect uri>"

freshBooksClient = FreshBooksClient(
    client_id=fb_client_id,
    client_secret=secret,
    redirect_uri=redirect_uri
)

authorization_url = freshBooksClient.get_auth_request_url(
    scopes=['user:profile:read', 'user:clients:read']
)
print(f"Go to this URL to authorize: {authorization_url}")

# Going to that URL will prompt the user to log into FreshBooks and authorize the application.
# Once authorized, FreshBooks will redirect the user to your `redirect_uri` with the authorization 
# code will be a parameter in the URL.
auth_code = input("Enter the code you get after authorization: ")

# This will exchange the authorization code for an access token
token_response = freshBooksClient.get_access_token(auth_code)
print(f"This is the access token the client is now configurated with: {token_response.access_token}")
print(f"It is good until {token_response.access_token_expires_at}")
print()

# Get the current user's identity
identity = freshBooksClient.current_user()
businesses = []

# Display all of the businesses the user has access to
for num, business_membership in enumerate(identity.business_memberships, start=1):
    business = business_membership.business
    businesses.append(
        SimpleNamespace(name=business.name, business_id=business.id, account_id=business.account_id)
    )
    print(f"{num}: {business.name}")
business_index = int(input("Which business do you want to use? ")) - 1
print()

business_id = businesses[business_index].business_id  # Used for project-related calls
account_id = businesses[business_index].account_id  # Used for accounting-related calls

# Get a client for the business to show successful access
client = freshBooksClient.clients.list(account_id)[0]
print(f"'{client.organization}' is a client of {businesses[business_index].name}")
