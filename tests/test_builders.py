from datetime import date, datetime
from freshbooks import PaginateBuilder, FilterBuilder, IncludesBuilder


class TestPaginateBuilder:

    def test_paginator_builder_calls(self):
        p = PaginateBuilder(page=1, per_page=3)
        assert p.build() == "&page=1&per_page=3"
        assert p.page() == 1
        assert p.per_page() == 3

        p.page(3)
        assert p.build() == "&page=3&per_page=3"

        p.per_page(5)
        assert p.build() == "&page=3&per_page=5"

        p.page(2).per_page(6)
        assert p.build() == "&page=2&per_page=6"

        p.per_page(2).page(6)
        assert p.build() == "&page=6&per_page=2"

        assert str(p) == "PaginateBuilder(page=6, per_page=2)"

    def test_minimum_page(self):
        p = PaginateBuilder(page=0)
        assert p.page() == 1

        p.page(0)
        assert p.page() == 1

        assert p.build() == "&page=1"

    def test_maximun_per_page(self):
        p = PaginateBuilder(per_page=500)
        assert p.per_page() == 100

        p.per_page(400)
        assert p.per_page() == 100

        assert p.build() == "&per_page=100"


class TestFilter:

    def test_boolean_true(self):
        filter = FilterBuilder()
        filter.boolean("active", True)

        assert filter.build() == "&active=True"
        assert str(filter) == "FilterBuilder(&active=True)"

    def test_boolean_false(self):
        filter = FilterBuilder()
        filter.boolean("active", False)

        assert filter.build() == "&active=False"

    def test_equals(self):
        filter = FilterBuilder()
        filter.equals("username", "Bob")

        assert filter.build() == "&search[username]=Bob"

    def test_in_list__plural(self):
        filter = FilterBuilder()
        filter.in_list("userids", [1, 2])

        assert filter.build() == "&search[userids][]=1&search[userids][]=2"

    def test_in_list__pluralized(self):
        filter = FilterBuilder()
        filter.in_list("userid", [1, 2])

        assert filter.build() == "&search[userids][]=1&search[userids][]=2"

    def test_like(self):
        filter = FilterBuilder()
        filter.like("user_like", "leaf")

        assert filter.build() == "&search[user_like]=leaf"

    def test_between_min_max(self):
        filter = FilterBuilder()
        filter.between("amount", 1, 10)

        assert filter.build() == "&search[amount_min]=1&search[amount_max]=10"

    def test_between_min_specified(self):
        filter = FilterBuilder()
        filter.between("amount_min", min=1)

        assert filter.build() == "&search[amount_min]=1"

    def test_between_max_specified(self):
        filter = FilterBuilder()
        filter.between("amount_max", max=10)

        assert filter.build() == "&search[amount_max]=10"

    def test_between_date_string(self):
        filter = FilterBuilder()
        filter.between("start_date", min="2020-10-17")

        assert filter.build() == "&search[start_date]=2020-10-17"

    def test_between_date_object(self):
        filter = FilterBuilder()
        filter.between("start_date", min=date(year=2020, month=10, day=17))

        assert filter.build() == "&search[start_date]=2020-10-17"

    def test_between_datetime_object(self):
        filter = FilterBuilder()
        filter.between("start_date", min=datetime(year=2020, month=10, day=17, hour=13, minute=14))

        assert filter.build() == "&search[start_date]=2020-10-17"


class TestInclude:

    def test_boolean_true(self):
        includes = IncludesBuilder()
        includes.include("late_reminders")

        assert includes.build() == "&include[]=late_reminders"
        assert str(includes) == "IncludesBuilder(&include[]=late_reminders)"
