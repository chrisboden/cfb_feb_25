.PHONY: sync deps dev

APP ?= agent:app
ENV_FILE ?= .env
RELOAD_DIR ?= .

sync:
	uv sync

deps: sync

dev: deps
	uv run --no-sync --env-file $(ENV_FILE) uvicorn $(APP) --reload --reload-dir $(RELOAD_DIR) --reload-include "*.html"
