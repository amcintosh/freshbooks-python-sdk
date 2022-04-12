# FreshBooks Python SDK Changelog

## Unreleased

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
