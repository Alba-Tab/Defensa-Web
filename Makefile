PYTHON ?= python3

.PHONY: install run migrate format lint typecheck test check

install:
	$(PYTHON) -m pip install -e './servicio[dev]'

run:
	$(PYTHON) -m uvicorn app.main:app --app-dir servicio --reload

migrate:
	$(PYTHON) -m alembic -c servicio/alembic.ini upgrade head

format:
	$(PYTHON) -m ruff format servicio
	$(PYTHON) -m ruff check --fix servicio

lint:
	$(PYTHON) -m ruff check servicio
	$(PYTHON) -m ruff format --check servicio

typecheck:
	$(PYTHON) -m mypy servicio/app

test:
	$(PYTHON) -m pytest servicio/tests

check: lint typecheck test
