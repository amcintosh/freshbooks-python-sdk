# This is an example where we create a new client and an invoice for them.

from datetime import date
from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError

FB_CLIENT_ID = "<your client id>"
ACCESS_TOKEN = "<your access token>"
ACCOUNT_ID = "<your account id>"

freshBooksClient = FreshBooksClient(client_id=FB_CLIENT_ID, access_token=ACCESS_TOKEN)

# Create the client
print("Creating client...")
try:
    client_data = {"organization": "Python SDK Test Client"}
    client = freshBooksClient.clients.create(ACCOUNT_ID, client_data)
except FreshBooksError as e:
    print(e)
    print(e.status_code)
    exit(1)

print(f"Created client {client.id}")

# Create the invoice
line1 = {
    "name": "Fancy Dishes",
    "description": "They're pretty swanky",
    "qty": 6,
    "unit_cost": {
        "amount": "27.00",
        "code": "CAD"
    }
}
line2 = {
    "name": "Regular Glasses",
    "description": 'They look "just ok"',
    "qty": 8,
    "unit_cost": {
        "amount": "5.95",
        "code": "CAD"
    }
}
invoice_data = {
    "customerid": client.id,
    "create_date": date.today().isoformat(),
    "due_offset_days": 5,  # due 5 days after create_date
    "lines": [line1, line2],
}
print("Creating invoice...")
try:
    invoice = freshBooksClient.invoices.create(ACCOUNT_ID, invoice_data)
except FreshBooksError as e:
    print(e)
    print(e.status_code)
    exit(1)

print(f"Created invoice {invoice.invoice_number} (Id: {invoice.id})")
print(f"Invoice total is {invoice.amount.amount} {invoice.amount.code}")

# Invoices are created in draft status, so we need to mark it as sent
print("Marking invoice as sent...")
invoice_data = {
    "action_mark_as_sent": True
}
try:
    invoice = freshBooksClient.invoices.update(ACCOUNT_ID, invoice.id, invoice_data)
except FreshBooksError as e:
    print(e)
    print(e.status_code)
    exit(1)
