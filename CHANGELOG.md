# FreshBooks Python SDK Changelog

## Unreleased

- Add Ledger Accounts resource
- Properly handle some project error messages
- `access_token_expires_at` is now set as UTC
- Handle new API version accounting and webhook event errors

## 1.2.1

- Improved error messages on authorization failures

## 1.2.0

- Add includes parameter to project-like `get` calls
- Allow API version header configuration
- Handle new API version accounting errors

## 1.1.0

- Added upload attachment and image resources
- Fixed `invoice_payment_options` create call (was not creating)
- Updated webhook event error handling for new FreshBooks API error strcuture
- Added list sort builder

## 1.0.1

- Fixed Identity "business_memberships" attribute to return Result objects

## 1.0.0

- Drop support for python 3.6 as it is end of life
- Added Bill Payments resource
- Added Service Rates resource
- Added Online Payments resource
- Additional configuration validation

## 0.8.0

- Added Bills and Bill Vendors APIs
- Allow includes for create, updates of accounting resources

## 0.7.1

- Fix equals filters for project-like resource

## 0.7.0

- (**BREAKING**) `client.current_user` is now a method, not a property for more consistency.
- Joining of ListResult objects with `__add__` to aid pagination of results, with example in README.

## 0.6.1

- Update documentation
- Minor test fixture updates
- Mark as Beta in pypi

## 0.6.0

- Date strings in Result objects now return as date and datetime objects. datetimes are zone-aware and normalized to UTC.
