.PHONY: env, install-dev
.PHONY: generate-docs, test

env:
	virtualenv -p python3.8 env

install-dev: env
	pip install -r requirements-dev.txt

generate-docs: install-dev
	rm -rf docs
	pdoc --html -o docs --force freshbooks
	mv docs/freshbooks/* docs/
	rm -rf docs/freshbooks/

test: install-dev
	mypy freshbooks
	py.test --junitxml=junit.xml \
		--cov=freshbooks \
		--cov-branch \
		--cov-report=xml:coverage.xml \
		tests
	coverage report -m
