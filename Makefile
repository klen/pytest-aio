VIRTUAL_ENV 	?= .venv

all: $(VIRTUAL_ENV)

$(VIRTUAL_ENV): uv.lock pyproject.toml
	@uv sync
	@uv run pre-commit install
	@touch $(VIRTUAL_ENV)

.PHONY: test t
test t: $(VIRTUAL_ENV)
	@uv run pytest tests

.PHONY: types
types: $(VIRTUAL_ENV)
	@uv run pyrefly check

.PHONY: ruff
ruff: $(VIRTUAL_ENV)
	@uv run ruff check

.PHONY: release
VPART?=minor
# target: release - Bump version
release:
	git checkout develop
	git pull
	git merge master
	uvx bump-my-version bump $(VPART)
	uv lock
	@VERSION="$$(uv version --short)"; \
	if git diff --quiet && git diff --cached --quiet; then \
	  echo "No changes to commit; skipping commit/tag"; \
	else \
		{ \
			printf 'build(release): %s\n\n' "$$VERSION"; \
			printf 'Changes:\n\n'; \
			git log --oneline --pretty=format:'%s [%an]' master..develop | grep -Evi 'github|^Merge' || true; \
		} | git commit -a -F -
	git tag "$$VERSION"
	git checkout master
	git pull
	git merge develop
	git checkout develop
	git push origin develop master
	git push origin --tags
	@echo "Release process complete for $$(VERSION)"

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VPART=patch

.PHONY: major
major:
	make release VPART=major

version v:
	uv version --short
