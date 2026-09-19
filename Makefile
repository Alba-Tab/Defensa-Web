PYTHON ?= python3

.PHONY: install run migrate format lint typecheck test infra-check mobile-check check check-all

install:
	$(PYTHON) -m pip install -e './servicio[dev,real]' -r ia/requirements.txt

run:
	$(PYTHON) -m uvicorn app.main:app --app-dir servicio --reload

migrate:
	$(PYTHON) -m alembic -c servicio/alembic.ini upgrade head

format:
	$(PYTHON) -m ruff format servicio ia
	$(PYTHON) -m ruff check --fix servicio ia
	cd movil && dart format lib test

lint:
	$(PYTHON) -m ruff check servicio ia
	$(PYTHON) -m ruff format --check servicio ia

typecheck:
	$(PYTHON) -m mypy servicio/app

test:
	$(PYTHON) -m pytest servicio/tests

infra-check:
	bash -n infra/provision/provision.sh infra/verificar.sh
	docker compose -f infra/compose/app-protegida.yaml config --quiet

mobile-check:
	cd movil && dart format --output=none --set-exit-if-changed lib test
	cd movil && flutter analyze
	cd movil && flutter test

check: lint typecheck test infra-check

check-all: check mobile-check
