venv-tools: requirements.tools.txt
	rm -rf venv-tools
	python -m venv venv-tools
	venv-tools/bin/pip install -r requirements.tools.txt

.PHONY: clean
clean:
	rm -rf venv-tools
