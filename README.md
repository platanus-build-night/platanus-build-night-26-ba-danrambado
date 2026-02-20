# Serendip Lab

AI-powered platform that creates intentional connections between people and opportunities.

*Platanus Build Night 26 — Buenos Aires — danrambado*

## Quick Start (Local)

```bash
# 1. Install dependencies
cd backend && uv sync && cd ..
cd frontend && npm install && cd ..

# 2. Set your Anthropic API key
cp .env.example .env
# Edit .env with your key

# 3. Seed the database
cd backend && uv run python seed.py && cd ..

# 4. Start both services (separate terminals)
make dev-backend   # http://localhost:8000
make dev-frontend  # http://localhost:3000
```

## Quick Start (Docker)

```bash
cp .env.example .env
# Edit .env with your key

docker-compose up --build
docker-compose exec backend uv run python seed.py

# Open http://localhost:3000
```

## Tech Stack

- **Backend:** Python + FastAPI + SQLAlchemy + SQLite + ChromaDB (managed with uv)
- **Frontend:** Next.js + Tailwind CSS + shadcn/ui
- **AI:** ChromaDB embeddings for fast retrieval, Anthropic Claude for ranking and explanations
- **Network effect:** Connections graph with 1st/2nd degree proximity scoring

## Architecture

Two-phase matching pipeline:
1. **Phase 1 (fast, ~50ms):** ChromaDB vector search -> filter by compatibility -> network proximity boost -> top 5
2. **Phase 2 (Claude, ~3s):** Rank top 5 candidates and generate personalized explanations referencing skills and network connections
