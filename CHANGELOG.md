# FreshBooks Python SDK Changelog

## Unreleased

## 0.7.1

- Fix equals filters for project-like resource

## 0.7.0

- *BREAKING* `client.current_user` is not a method, not a property for more consistency.
- Joining of ListResult objects with `__add__` to aid pagination of results, with example in README.

## 0.6.1

- Update documentation
- Minor test fixture updates
- Mark as Beta in pypi

## 0.6.0

- Date strings in Result objects now return as date and datetime objects. datetimes are zone-aware and normalized to UTC.
