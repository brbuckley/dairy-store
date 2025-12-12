# Dairy Store

```sh
# spin up postgres
docker run --rm --name dairy-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=dairy -e POSTGRES_HOST_AUTH_METHOD=trust -p 5432:5432 -d postgres

# run migrations
alembic upgrade head

# uv python manager
pip install uv
uv sync
.venv/Scripts/activate

# running the server
uvicorn app.__main__:app
python -m app app

# tests
python -m pytest -s tests/integration/api/test_create_batches.py
locust -f .\tests\end_to_end\locustfile.py
```

