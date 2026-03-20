.PHONY: dev dev-backend dev-frontend build up down logs test

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "请在两个终端分别运行:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	cd backend && uv run pytest tests/ -v
