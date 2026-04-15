PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

.PHONY: install dev test smoke init-env docker-up docker-down

install:
	$(PIP) install -r requirements.txt

dev:
	$(PYTHON) run.py

test:
	$(PYTHON) -m unittest tests/test_app.py

smoke:
	$(PYTHON) scripts/smoke_check.py

init-env:
	cp -n .env.example .env || true

docker-up:
	docker compose up --build

docker-down:
	docker compose down
