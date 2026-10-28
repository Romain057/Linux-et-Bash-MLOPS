.PHONY: bash tests all

PYTHON := .venv/bin/python

bash:
	bash scripts/collect.sh
	bash scripts/preprocessed.sh
	bash scripts/train.sh

tests:
	$(PYTHON) -m pytest tests/test_collect.py
	$(PYTHON) -m pytest tests/test_preprocessed.py
	$(PYTHON) -m pytest tests/test_model.py

all: bash tests