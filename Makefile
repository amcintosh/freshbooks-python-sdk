.PHONY: env, install-dev, tag, clean
.PHONY: generate-docs, test, check-style, check-types

PROJECT=freshbooks-python-sdk
GIT_URL="https://${GIT_CREDENTIALS_USR}:${GIT_CREDENTIALS_PSW}@github.com/freshbooks/$(PROJECT).git"
GIT_RELEASE_WORKING_DIR=/tmp/$(PROJECT)

ifeq ($(BRANCH_NAME),)
BRANCH_NAME="$$(git rev-parse --abbrev-ref HEAD)"
endif

env:
	virtualenv -p python3.8 env

install-dev: env
	pip install -r requirements-dev.txt

generate-docs:
	rm -rf docs
	pdoc --html -o docs --force freshbooks
	mv docs/freshbooks/* docs/
	rm -rf docs/freshbooks/

tag:
	@if [ "$(BRANCH_NAME)" != "master" ]; then \
		echo "You must be on master to update the version"; \
		exit 1; \
	fi;
	@if [ "$(VERSION_PART)" = '' ]; then \
		echo "Must specify VERSION_PART to bump (major, minor, patch)."; \
		exit 1; \
	fi;
	pip install bumpversion
	./scripts/update_changelog.sh $(VERSION_PART)
	git add CHANGELOG.md && \
	git commit -m "🔖 Update CHANGELOG for release" && \
	git push origin master
	git stash && \
	git fetch --all && \
	git reset --hard origin/master && \
	bumpversion $(VERSION_PART) && \
	git push origin --tags && \
	git push origin master && \
	git stash pop

check-style:
	flake8 freshbooks --count --show-source --statistics
	flake8 tests --count --show-source --statistics

check-types:
	mypy --install-types --non-interactive freshbooks

test:
	py.test --junitxml=junit.xml \
		--cov=freshbooks \
		--cov-branch \
		--cov-report=xml:coverage.xml \
		--cov-config=setup.cfg \
		tests
	coverage report -m

test-all: test check-style check-types
