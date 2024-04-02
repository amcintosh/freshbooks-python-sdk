# Webhook Callbacks

The client supports registration and verification of FreshBooks' API Webhook Callbacks.
See [FreshBooks' documentation](https://www.freshbooks.com/api/webhooks) for more information.

FreshBooks will send webhooks as a POST request to the registered URI with form data:

```http
name=invoice.create&object_id=1234567&account_id=6BApk&business_id=6543&identity_id=1234user_id=1
```

## Registration

```python
data = {
    "event": "invoice.create",
    "uri": "http://your_server.com/webhooks/ready"
}

webhook = freshBooksClient.callbacks.create(account_id, data)

assert webhook.callback_id == 2001
assert webhook.verified == False
```

## Registration Verification

Registration of a webhook will cause FreshBooks to send a webhook to the specified URI with a
verification code. The webhook will not be active until you send that code back to FreshBooks.

```python
freshBooksClient.callbacks.verify(account_id, callback_id, verification_code)
```

If needed, you can ask FreshBooks to resend the verification code.

```python
freshBooksClient.callbacks.resend_verification(account_id, callback_id)
```

Hold on to the verification code for later use (see below).

## Verifing Webhook Signature

Each Webhook sent by FreshBooks includes a header, `X-FreshBooks-Hmac-SHA256`, with a base64-encoded
signature generated from a JSON string of the form data sent in the request and hashed with the token
originally sent in the webhook verification process as a secret.

From FreshBooks' documentation, the signature can be generated in Python using:

```python
# Using Flask
import base64
import hmac
import hashlib
import json

from flask import Flask, request

def signature_match(verifier, request):
   signature = request.headers.get('X-FreshBooks-Hmac-SHA256')
   data = json.dumps(request.form)

   dig = hmac.new(
      verifier.encode('utf-8'),
      msg=data.encode('utf-8'),
      digestmod=hashlib.sha256
   ).digest()
   calculated_sig = base64.b64encode(dig).decode()

   return signature == calculated_sig
```
