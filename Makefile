DEFAULT_GOAL := ci

.PHONY: ci
ci: check format-check test

.venv: uv.lock pyproject.toml
	rm -rf .venv
	uv sync

.PHONY: venv
venv: .venv

.PHONY: clean
clean:
	rm -rf .venv
	rm -rf dist

.PHONY: test
test: venv
	uv run pytest

.PHONY: format
format: venv-tools
	uv run ruff check --fix --unsafe-fixes
	uv run ruff format

.PHONY: format-check
format-check:
	uv run ruff check
	uv run ruff format --check

.PHONY: check
check: venv
	uv run ty check
