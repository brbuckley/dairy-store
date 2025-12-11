from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.admin_endpoints import router as admin_router
from app.api.batch_endpoints import router as batch_router

app = FastAPI()
app.include_router(batch_router)
app.include_router(admin_router)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema  # type: ignore

    openapi_schema = get_openapi(
        title="dairy-store",
        version="0.0.1",
        description="Dairy Store",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema

    return app.openapi_schema  # type: ignore


app.openapi = custom_openapi  # type: ignore

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
