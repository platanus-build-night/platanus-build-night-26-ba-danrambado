.PHONY: install dev seed dev-backend dev-frontend clean lint test docker-up docker-down docker-seed prod-up prod-down prod-build prod-seed prod-logs

install:
	cd backend && uv sync
	cd frontend && npm install

dev-backend:
	cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting backend and frontend..."
	@make dev-backend & make dev-frontend

seed:
	cd backend && uv run python seed.py

clean:
	rm -rf backend/data
	rm -rf frontend/.next
	rm -rf frontend/node_modules

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .
	cd frontend && npm run lint

test:
	cd backend && uv run pytest -q

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

docker-seed:
	docker-compose exec backend uv run python seed.py

# ── Production (VPS) ──────────────────────────────────────────────────────────
prod-up:
	docker compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-build:
	docker compose -f docker-compose.prod.yml build

prod-seed:
	docker compose -f docker-compose.prod.yml exec backend uv run python seed.py

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f
