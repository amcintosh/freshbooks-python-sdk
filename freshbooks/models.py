class Result:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __str__(self):
        return "Result({})".format(self.name)

    def __getattr__(self, name):
        return self.data.get(name)


class ListResult:
    def __init__(self, list_name, single_name, data):
        self.list_name = list_name
        self.single_name = single_name
        self.data = data

    def __str__(self):
        return "Result({})".format(self.list_name)

    def __len__(self):
        return len(self.data.get(self.list_name, []))

    def __getitem__(self, index):
        results = self.data.get(self.list_name, [])
        return Result(self.single_name, results[index])

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        results = self.data.get(self.list_name, [])
        if self.n < len(results):
            result = Result(self.single_name, results[self.n])
            self.n += 1
            return result
        else:
            raise StopIteration
