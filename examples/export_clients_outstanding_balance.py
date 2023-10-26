# This is an example where we fetch all clients and their outstanding balances and export
# them to a csv file.
# It demostrates pagination and extra included fields.

# Each csv row will contain the outstanding balance for a particular currency for a client.
# Thus clients with multiple currencies will have multiple rows.
# Eg.
# 123, Bob, 200, CAD
# 123, Bob, 100, USD
# 456, Alice, 300, CAD

import csv

from freshbooks import Client as FreshBooksClient
from freshbooks import FreshBooksError, IncludesBuilder, PaginateBuilder

FB_CLIENT_ID = "<your client id>"
ACCESS_TOKEN = "<your access token>"
ACCOUNT_ID = "<your account id>"
PAGE_SIZE = 100

freshBooksClient = FreshBooksClient(client_id=FB_CLIENT_ID, access_token=ACCESS_TOKEN)

with open("clients.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Client Id", "Organization", "Outstanding Balance", "Currency"])

    print("Fetching all clients...")
    # Setup paginator to iterate through all clients
    paginator = PaginateBuilder(1, PAGE_SIZE)
    # Include outstanding balances in the response
    includes = IncludesBuilder().include("outstanding_balance")

    clients = None
    while not clients or clients.pages.page < clients.pages.pages:
        try:
            # Get page of clients with outstanding balance included
            clients = freshBooksClient.clients.list(ACCOUNT_ID, builders=[paginator, includes])
        except FreshBooksError as e:
            print(e)
            print(e.status_code)
            exit(1)

        for client in clients:
            print(f"Writing client {client.organization} ({client.id}) to csv...")
            # Clients will have a outstanding_balance for each currency
            if not client.outstanding_balance:
                writer.writerow([client.id, client.organization])
            else:
                for outstanding_balance in client.outstanding_balance:
                    writer.writerow([
                        client.id,
                        client.organization,
                        outstanding_balance.amount.amount,
                        outstanding_balance.amount.code
                    ])

        # Update paginator to get next page
        paginator.page(clients.pages.page + 1)
