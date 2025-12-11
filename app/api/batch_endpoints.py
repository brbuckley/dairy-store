from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.config.dependency_injection import BatchServiceDep
from app.schemas.batches_schema import Batch

router = APIRouter()


# Request body for POST /api/batches/{id}/consume
class ConsumeRequest(BaseModel):
    qty: float = Field(
        ...,
        ge=0,
    )
    order_id: str | None = None


@router.post(
    "/api/batches",
    response_model=Batch,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    request: Batch,
    service: BatchServiceDep,
) -> Batch:
    return service.create(request)


@router.get(
    "/api/batches",
    response_model=list[Batch],
)
async def list_all(
    service: BatchServiceDep,
) -> list[Batch]:
    return service.list_all()


@router.get(
    "/api/batches/near-expiry",
    response_model=list[Batch],
)
async def list_near_expiry(
    service: BatchServiceDep,
    n_days: int = Query(ge=1, description="Number of days until expiry"),
) -> list[Batch]:
    """List batches that will expire within the next n_days."""
    return service.list_near_expiry(n_days=n_days)


@router.get(
    "/api/batches/{id}",
    response_model=Batch,
)
async def read_by_id(
    id: int,
    service: BatchServiceDep,
) -> Batch:
    try:
        batch = service.read_by_id(id)
    except Exception as error:
        raise HTTPException(404, f"Batch {id} not found") from error
    return batch


@router.post(
    "/api/batches/{id}/consume",
    response_model=Batch,
    status_code=status.HTTP_200_OK,
)
async def consume(
    id: int,
    request: ConsumeRequest,
    service: BatchServiceDep,
) -> Batch:
    """
    Safely consume liters from a batch.

    Body example:
    {
        "qty": 10.5,
        "order_id": "ORD-12345"
    }
    """
    try:
        return service.consume(
            batch_id=id,
            qty=request.qty,
            order_id=request.order_id,
        )
    except Exception as error:
        raise HTTPException(
            500, f"Batch {id} is locked, try again later"
        ) from error


@router.delete(
    "/api/batches/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    id: int,
    service: BatchServiceDep,
) -> None:
    """
    Soft-delete a batch by id.
    Returns 204 No Content on success.
    """
    service.delete(id)
