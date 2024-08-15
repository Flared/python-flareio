venv: pyproject.toml poetry.lock venv-tools
	rm -rf venv
	python3 -m venv venv
	venv-tools/bin/poetry install

venv-tools: requirements.tools.txt
	rm -rf venv-tools
	python3 -m venv venv-tools
	venv-tools/bin/pip install -r requirements.tools.txt

.PHONY: clean
clean:
	rm -rf venv
	rm -rf venv-tools

.PHONY: test
test: venv
	venv/bin/pytest

.PHONY: build
build: venv-tools
	rm -rf dist
	venv-tools/bin/poetry build
