# inventory-api

[![Tests](https://github.com/Ritzxo/inventory-api/actions/workflows/tests.yml/badge.svg)](https://github.com/Ritzxo/inventory-api/actions/workflows/tests.yml)

A small REST API for managing inventory, built with Python and FastAPI.

This started as a command-line script in my [python-practice](https://github.com/Ritzxo/python-practice)
repo. I'm rebuilding it as a proper service: validated input, correct HTTP status codes,
a real database, tests and CI.

**Status: in progress.** See the roadmap below for what works today.

## Run it locally

Requires Python 3.12+.

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Then open <http://127.0.0.1:8000/docs> for the interactive API documentation.

## Run the tests

```bash
pytest -v
```

The tests cover every endpoint, including the error cases. A failed sale or stock update
must leave stored data unchanged. They also run automatically on every push through
GitHub Actions.

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
- [ ] Persistent storage with SQLite and SQLAlchemy
- [ ] Switch to Postgres and run everything with Docker Compose
