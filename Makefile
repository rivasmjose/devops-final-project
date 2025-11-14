.PHONY: info build pull up down restart logs clean test lint

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

info:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' app
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' db
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pgadmin

build:
	docker compose $(COMPOSE_FILE) build

pull:
	docker compose $(COMPOSE_FILE) pull

up:
	docker compose $(COMPOSE_FILE) up -d

down:
	docker compose $(COMPOSE_FILE) down -v

restart: down up

logs:
	docker compose $(COMPOSE_FILE) logs -f

clean:
	docker container prune -f
	docker network prune -f
	docker volume prune -f

test:
	docker compose $(COMPOSE_FILE) run --rm app pytest -q

lint:
	docker compose $(COMPOSE_FILE) run --rm app flake8 app
