#!/bin/bash

# Update "Unreleased" CHANGELOG notes on release

VERSION="$(bumpversion --dry-run --list $1 | grep -E 'new_version=[0-9\.]+' | grep -oE '[0-9\.]+')"
sed -i '' 's/## Unreleased/## Unreleased\
\
## '"${VERSION}/" ./CHANGELOG.md
