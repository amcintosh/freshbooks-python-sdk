class Result:
    """Result object from API calls with a single resource returned.

    Data in the API can be accessed via attributes.

    Example:
    ```python
    client = FreshBooksClient.clients.get(account_id, user_id)
    assert client.organization == "FreshBooks"
    assert client.userid == user_id
    ```

    The json-parsed dictionary can also be directly accessed via the `data` attribute.

    Example:
    ```python
    assert client.data['organization'] == "FreshBooks"
    assert client.data['userid'] == user_id
    ```
    """

    def __init__(self, name, data):
        self.name = name
        self.data = data[name]

    def __str__(self):
        return "Result({})".format(self.name)

    def __getattr__(self, field):
        return self.data.get(field)


class ListResult:
    """Result object from API calls with a list of resources returned.

    Data in the API can be accessed via attributes.

    Example:
    ```python
    clients = FreshBooksClient.clients.list(account_id)
    assert clients[0].organization == "FreshBooks"
    ```

    The json-parsed dictionary can also be directly accessed via the `data` attribute.

    Example:
    ```python
    assert clients.data["clients"][0]["organization"] == "FreshBooks"
    ```

    The list can also be iterated over to access the individual resources as `Result` obejcts.

    Example:
    ```python
    for client in clients:
        assert client.organization == "FreshBooks"
        assert client.data['organization'] == "FreshBooks"
    ```
    """

    def __init__(self, name, single_name, data):
        self.name = name
        self.single_name = single_name
        self.data = data

    def __str__(self):
        return "Result({})".format(self.name)

    def __len__(self):
        return len(self.data.get(self.name, []))

    def __getitem__(self, index):
        results = self.data.get(self.name, [])
        return Result(self.single_name, results[index])

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        results = self.data.get(self.name, [])
        if self.n < len(results):
            result = Result(self.single_name, {self.single_name: results[self.n]})
            self.n += 1
            return result
        else:
            raise StopIteration
