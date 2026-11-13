# inventory-api

[![Tests](https://github.com/Ritzxo/inventory-api/actions/workflows/tests.yml/badge.svg)](https://github.com/Ritzxo/inventory-api/actions/workflows/tests.yml)

A small REST API for managing inventory, built with Python and FastAPI.

This started as a command-line script in my [python-practice](https://github.com/Ritzxo/python-practice)
repo. I'm rebuilding it as a proper service: validated input, correct HTTP status codes,
a real database, tests and CI.

**Status: complete.** Everything on the roadmap below is built and tested.

## Run everything with Docker Compose

Requires Docker Desktop. This starts Postgres and the API together; you don't need
Python installed.

```bash
# create your local settings file, then edit .env and set your own password
# Windows (PowerShell):
Copy-Item .env.example .env
# macOS / Linux:
# cp .env.example .env

docker compose up --build
```

Then open <http://127.0.0.1:8000/docs> for the interactive API documentation. The API
container creates the `items` table on startup if it doesn't exist yet. Stop everything
with Ctrl+C, or `docker compose down` (your data is kept in the `pgdata` volume).

## Run the API on your machine (for development)

Requires Python 3.12+ and Docker Desktop (for Postgres).

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# create .env as above, then start only the database
docker compose up -d db

# create the items table (once)
python database.py

uvicorn main:app --reload
```

## Configuration

Settings are read from environment variables, loaded from a `.env` file if there is one.
`.env` is ignored by git, so passwords stay out of the repository; `.env.example` shows
what to set.

| Variable | Used by | Purpose |
|---|---|---|
| `DATABASE_URL` | `database.py` | How the API connects to Postgres when run on your machine |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | `docker-compose.yml` | Create the Postgres user and database, and build the API container's connection URL |

Inside Docker Compose the API reaches the database by its service name (`db`), not
`localhost`, so Compose gives the container its own `DATABASE_URL`.

## Run the tests

```bash
pytest -v
```

The tests cover every endpoint, including the error cases. A failed sale or stock update
must leave stored data unchanged, and invalid item names (empty, only spaces, or
containing `/`) are rejected. The tests use a throwaway SQLite database, so Postgres
doesn't need to be running. On every push, GitHub Actions runs the tests and also checks
that the Docker image builds.

## API design

The planned endpoints, status codes and the reasoning behind them are in
[DESIGN.md](DESIGN.md).

## Roadmap

- [x] Project setup, virtual environment, health check endpoint
- [x] `POST /items` with pydantic validation
- [x] `GET /items/{name}`
- [x] `PATCH /items/{name}`
- [x] `POST /sales` (atomic, all-or-nothing)
- [x] Automated tests with pytest, run in GitHub Actions
- [x] Persistent storage with SQLite and SQLAlchemy
- [x] Switch to Postgres
- [x] Validate item names (no empty names, no `/`)
- [x] Settings from environment variables; no password in the code
- [x] Dockerfile for the API, and run everything with Docker Compose
