# API design

This document describes the endpoints for the inventory service. It replaces the
original command-line script (`inventory_management.py` in my
[python-practice](https://github.com/Ritzxo/python-practice) repo), which kept state in a
global dictionary and reported errors with `print`.

## Goals

- Expose inventory operations over HTTP so any client can use them.
- Validate input at the edge (no negative stock or prices, correct types).
- Use proper HTTP status codes instead of printed messages.
- Make bulk operations all-or-nothing (atomic).

## Endpoints

| Method | Path | Purpose | Success |
|---|---|---|---|
| `POST` | `/items` | Add a new item | `201 Created` |
| `GET` | `/items/{name}` | Check an item's details and stock | `200 OK` |
| `PATCH` | `/items/{name}` | Change an item's stock by a relative amount | `200 OK` |
| `POST` | `/sales` | Record a sale of one or more items | `200 OK` |

### `POST /items`

Request body:

```json
{"name": "Apple", "price": 0.5, "stock": 50}
```

| Status | Meaning |
|---|---|
| `201` | Item created; response body is the stored item |
| `409` | An item with that name already exists |
| `422` | Invalid input (wrong type, negative price or stock, or an invalid name) |

### `GET /items/{name}`

No request body.

| Status | Meaning |
|---|---|
| `200` | Response body is the item: `{"name": "Apple", "price": 0.5, "stock": 50}` |
| `404` | No item with that name |

### `PATCH /items/{name}`

Request body (a relative change; negative values remove stock):

```json
{"change": -5}
```

| Status | Meaning |
|---|---|
| `200` | Response body is the updated item |
| `404` | No item with that name |
| `409` | The change would take stock below zero |
| `422` | `change` is not an integer |

### `POST /sales`

Request body:

```json
{"items": {"Apple": 30, "Banana": 20}}
```

| Status | Meaning |
|---|---|
| `200` | Response body: `{"total_revenue": 21.0}`; stock is reduced |
| `404` | One of the items does not exist; no stock is changed |
| `409` | One of the items has insufficient stock; no stock is changed |
| `422` | Invalid input (quantity not an integer, or negative) |

## Design decisions

- **Item name is the identifier for now.** It mirrors the original script. A database
  with numeric ids may replace this later.
- **Names are validated because they appear in URLs.** Since the name is part of
  `/items/{name}`, a name must not be empty (after trimming spaces), must be at most 100
  characters, and must not contain `/`. A name like `a/b` could be created but never
  fetched or updated, because the slash splits the URL path.
- **`PATCH` for stock changes** because only one field changes; `PUT` would replace the
  whole item. The field is called `change` rather than `quantity` to make clear it is
  added to the current stock, not set.
- **Sales are all-or-nothing.** The original script skipped bad items and carried on,
  which leaves the caller guessing which parts succeeded. Rejecting the whole request
  (atomicity) is safer and easier to reason about.
- **Errors use status codes, not return values.** The original `check_availability`
  returned either a number or the string "Item not found". Now failure is a `404`.
- **Storage started in memory** and moved to SQLite, then Postgres, one step at a time,
  so each swap was visible and the API layer stayed independent of storage.
- **Settings come from the environment.** The database URL and password are read from
  environment variables (loaded from a git-ignored `.env` file), not written in the code.
  Tables are created by an explicit step (`python database.py`, which the Docker image
  runs on startup), not as a side effect of importing the code, so tests and tools can
  import the app without a database.
