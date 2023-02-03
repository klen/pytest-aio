VIRTUAL_ENV 	?= env

all: $(VIRTUAL_ENV)

$(VIRTUAL_ENV): requirements/requirements.txt requirements/requirements-tests.txt
	@[ -d $(VIRTUAL_ENV) ] || python -m venv $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pip install -e .[build,tests]
	@touch $(VIRTUAL_ENV)

VERSION	?= minor

.PHONY: version
version: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pip install bump2version
	$(VIRTUAL_ENV)/bin/bump2version $(VERSION)

.PHONY: release
release:
	git checkout master
	git pull
	git merge develop
	git checkout develop
	git push origin develop master
	git push --tags

.PHONY: minor
minor:
	make version VERSION=minor

.PHONY: patch
patch:
	make version VERSION=patch

.PHONY: major
major:
	make version VERSION=major


.PHONY: clean
# target: clean - Display callable targets
clean:
	rm -rf build/ dist/ docs/_build *.egg-info
	find $(CURDIR) -name "*.py[co]" -delete
	find $(CURDIR) -name "*.orig" -delete
	find $(CURDIR)/$(MODULE) -name "__pycache__" | xargs rm -rf


test t: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pytest tests


mypy: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/mypy pytest_aio
