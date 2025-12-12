# 🥛 Dairy Store

Dairy Store is a FastAPI-based system that manages milk batch inventory, shelf-life expiration, and safe consumption workflows for dairy processing facilities.

This project is an implementation exercise based on operational requirements from Schreiber Foods, designed to simulate realistic production constraints: concurrency, accuracy, auditability, expiry tracking, and consistency under load.

## 📦 Features

- Batch registration (milk deliveries)

- Accurate expiry calculation using normalized UTC timestamps

- Safe consumption with checks to prevent over-consumption

- Optimistic concurrency control via versioning

- Soft-delete instead of hard deletion

- Near-expiry listings for production planning

- Complete audit trail of consumption records

- Full integration test suite

- Optional load testing via Locust

## 🧱 Project Structure

Dairy Store follows lightweight DDD principles:

```
app/
 ├── api/               # FastAPI routes
 ├── domain/            # Ports, services, domain rules (pure logic)
 ├── repositories/      # Modular access to data (DB and in-memory)
 ├── schemas/           # Pydantic schemas
 └── config/            # dependency injection, settings
tests/
 ├── end_to_end/        # End to End and Concurrency tests
 └── integration/       # Business logic tests
```

## 🧪 Testing Strategy

Integration tests (pytest) validate all API endpoints end-to-end. Concurrency testing uses threading to issue simultaneous consume requests. Locust load tests simulate thousands of requests.

Tests cover:

- Batch creation

- Listing & filtering

- Consumption rules

- Concurrency failures

- Near-expiry calculations

- Soft deletes

- Audit records

## 🚀 Getting Started
1. Clone the repository
`git clone https://github.com/brbuckley/dairy-store`
`cd dairy-store`

2. Spin up PostgreSQL
```
docker run --rm --name dairy-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=dairy \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -p 5432:5432 -d postgres
```

3. Install dependencies

We recommend using uv (ultra-fast package manager):
```
pip install uv
uv sync
.venv/Scripts/activate   # Windows
# or source .venv/bin/activate (macOS/Linux)
```
4. Run database migrations
`alembic upgrade head`


This applies table creation migrations and seed data migrations (initial batches, if configured)

5. Run the API server

Either via uvicorn:

`uvicorn app.__main__:app --reload`


Or via Python module:

`python -m app app`


Server runs on http://localhost:8000


## 🧪 Running Tests

Run a specific test:
`python -m pytest -s tests/integration/api/test_create_batches.py`

Load testing (needs the server running on 8000)
`locust -f tests/end_to_end/locustfile.py`


Then open:
👉 http://localhost:8089

This allows high-concurrency testing of the consume endpoint and verifies your optimistic locking.

## ⚙️ Environment Variables

The system reads settings via Pydantic:
```
DAIRY_STORE_ENV=dev
DAIRY_STORE_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/dairy
```

Defaults work out-of-the-box for local development.

## 🔒 Concurrency Control

To ensure safe, race-free updates when multiple operators or automated systems modify the same batch, the Dairy Store implements optimistic concurrency control (OCC).
This prevents issues such as over-consumption, lost updates, two workers modifying the same batch simultaneously, and inconsistent inventory states

### How it Works

Each Batch domain object contains a private `_version` field, this version number is incremented every time the batch is updated. Before commiting the update we check if the version saved in the DB is higher than the one we're trying to create, if so, it retries the operation from the start, fetching the most recent version and updating from there. The number of retries and the backoff period between each try is configurable.

This ensures that:

- Only the latest known state can be modified.

- Parallel updates detect conflicts instead of overwriting each other.

- High read/write throughput is maintained (no DB row-level locking required).



## 🏗️ Future Work

- Pagination and filtering on list endpoints

- Structured logging with correlation IDs

- Domain value objects for Volume and BatchCode

- Reserve-liters concept for planned production

- Small search UI or a script simulating concurrent consume attempts
