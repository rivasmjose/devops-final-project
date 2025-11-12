.PHONY: build up down restart logs test lint

ENV ?= dev

ifeq ($(ENV),dev)
	COMPOSE_FILE=-f compose.yml -f compose.dev.yml
endif
ifeq ($(ENV),stage)
	COMPOSE_FILE=-f compose.yml -f compose.stage.yml
endif
ifeq ($(ENV),prod)
	COMPOSE_FILE=-f compose.yml -f compose.prod.yml
endif

build:
	docker compose $(COMPOSE_FILE) build

up:
	docker compose $(COMPOSE_FILE) up -d

down:
	docker compose $(COMPOSE_FILE) down

restart: down up

logs:
	docker compose $(COMPOSE_FILE) logs -f

test:
	docker compose $(COMPOSE_FILE) run --rm app pytest -q

lint:
	docker compose $(COMPOSE_FILE) run --rm app flake8 app
