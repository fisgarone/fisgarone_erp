.PHONY: install fmt lint test dev-up dev-down migrate

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

fmt:
	ruff check --fix .
	ruff format .
	black .
	isort .

lint:
	ruff check .
	mypy app

test:
	pytest -q --maxfail=1 --disable-warnings

dev-up:
	docker compose up -d --build

dev-down:
	docker compose down -v

migrate:
	docker compose run --rm migrate
