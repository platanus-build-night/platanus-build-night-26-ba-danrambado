.PHONY: install dev seed dev-backend dev-frontend clean docker-up docker-down docker-seed

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

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

docker-seed:
	docker-compose exec backend uv run python seed.py
