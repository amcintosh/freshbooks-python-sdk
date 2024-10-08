# FreshBooks Python SDK

[![PyPI](https://img.shields.io/pypi/v/freshbooks-sdk)](https://pypi.org/project/freshbooks-sdk/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/freshbooks-sdk)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/amcintosh/freshbooks-python-sdk/Run%20Tests)](https://github.com/amcintosh/freshbooks-python-sdk/actions?query=workflow%3A%22Run+Tests%22)

The FreshBooks Python SDK allows you to more easily utilize the [FreshBooks API](https://www.freshbooks.com/api).

## Installation

```bash
pip install freshbooks-sdk
```

## Usage

See the [full documentation](https://freshbooks-python-sdk.readthedocs.io/) or check out some of our [examples](https://github.com/amcintosh/freshbooks-python-sdk/tree/main/examples).

## Development

### Testing

To run all tests:

```bash
make test
```

To run a single test with pytest:

```bash
py.test path/to/test/file.py
py.test path/to/test/file.py::TestClass::test_case
```

### Documentations

You can generate the documentation via:

```bash
make generate-docs
```
