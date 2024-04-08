VIRTUAL_ENV 	?= .venv

all: $(VIRTUAL_ENV)

$(VIRTUAL_ENV): poetry.lock
	@[ -d $(VIRTUAL_ENV) ] || python -m venv $(VIRTUAL_ENV)
	@poetry install --with dev
	@poetry self add poetry-bumpversion
	@poetry run pre-commit install
	@touch $(VIRTUAL_ENV)

.PHONY: test t
test t: $(VIRTUAL_ENV)
	@poetry run pytest tests

.PHONY: mypy
mypy: $(VIRTUAL_ENV)
	@poetry run mypy

.PHONY: ruff
ruff: $(VIRTUAL_ENV)
	@poetry run ruff check pytest_aio

VERSION	?= minor

#  Bump version
# ==============

.PHONY: release
VERSION?=minor
# target: release - Bump version
release:
	@git checkout master
	@git pull
	@git merge develop
	@poetry version $(VERSION)
	@git commit -am "build(release): `poetry version -s`"
	@git tag `poetry version -s`
	@git checkout develop
	@git merge master
	@git push origin develop master
	@git push --tags

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch

.PHONY: major
major:
	make release VERSION=major
