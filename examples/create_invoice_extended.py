# This is an example where we create a customized invoice with logos and attachments,
# and a payment gateway, then send it by email to your address.

from datetime import date
from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError

FB_CLIENT_ID = "<your client id>"
ACCESS_TOKEN = "<your access token>"
ACCOUNT_ID = "<your account id>"
DESTINATION_EMAIL = "<your email>"  # Don't use the same email as the account owner.

freshBooksClient = FreshBooksClient(client_id=FB_CLIENT_ID, access_token=ACCESS_TOKEN)

# Create the client
print("Creating client...")
try:
    client_data = {
        "email": DESTINATION_EMAIL,
        "organization": "Python SDK Test Client"
    }
    client = freshBooksClient.clients.create(ACCOUNT_ID, client_data)
except FreshBooksError as e:
    print(e)
    print(e.status_code)
    exit(1)

print(f"Created client {client.id}")

# Upload a logo and attachment with examples of file_path and file_stream.
try:
    print("Uploading invoice logo")
    # We upload a file by providing the path to the file.
    logo = freshBooksClient.images.upload(ACCOUNT_ID, file_path="./assets/sample_logo.png")

    print("Uploading invoice attachment")
    # We upload a file by opening it and providing the file stream.
    attachment = freshBooksClient.attachments.upload(
        ACCOUNT_ID, file_stream=open("./assets/sample_attachment.pdf", "rb")
    )
except FreshBooksError as e:
    print(e)
    print(e.status_code)
    exit(1)

# Create the invoice with taxed line items, a custom colour and logo, and an attachment.

# Taxed line items
line1 = {
    "name": "A Taxed Item",
    "description": "These things are taxed",
    "qty": 2,
    "taxAmount1": "13",
    "taxName1": "HST",
    "unit_cost": {
        "amount": "27.00",
        "code": "CAD"
    }
}
line2 = {
    "name": "Another Taxed ItemRegular Glasses",
    "description": "With a different tax",
    "qty": 4,
    "taxAmount1": "5",
    "taxName1": "GST",
    "unit_cost": {
        "amount": "6.95",
        "code": "CAD"
    }
}

presentation = {
    "theme_primary_color": "#1fab13",
    "theme_layout": "simple",
    "theme_font_name": "modern",
    "image_logo_src": f"/uploads/images/{logo.jwt}"  # The logo upload response contains a jwt token
}

invoice_data = {
    "customerid": client.id,
    "create_date": date.today().isoformat(),
    "due_offset_days": 5,
    "lines": [line1, line2],
    "attachments": [
        {
            "jwt": attachment.jwt,
            "media_type": attachment.media_type
        }
    ],
    "presentation": presentation
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

# Once the invoice is created, a payment option can be added to it.
print("Adding fbpay payment option...")
payment_option_data = {
    "gateway_name": "fbpay",
    "entity_id": invoice.id,
    "entity_type": "invoice",
    "has_credit_card": True
}
try:
    freshBooksClient.invoice_payment_options.create(ACCOUNT_ID, invoice.id, payment_option_data)
except FreshBooksError as e:
    print(e)
    print(e.status_code)
    exit(1)

# Invoices are created in draft status, so we need to send it.
print("Sending the invoice by email...")
invoice_data = {
    "action_email": True,
    "email_recipients": [destination_email],
    "email_include_pdf": False,
    "invoice_customized_email": {
        "subject": "Test Styled Invoice",
        "body": "This was an example",
    }
}
try:
    invoice = freshBooksClient.invoices.update(ACCOUNT_ID, invoice.id, invoice_data)
except FreshBooksError as e:
    print(e)
    print(e.status_code)
    exit(1)
