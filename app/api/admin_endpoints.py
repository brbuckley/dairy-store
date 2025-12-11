
from fastapi import APIRouter

from app.config.dependency_injection import AdminServiceDep
from app.schemas.batches_schema import Batch
from app.schemas.consumption_record import ConsumptionRecord

router = APIRouter()


@router.get(
    "/admin/records",
    response_model=list[ConsumptionRecord],
)
async def list_all_records(
    service: AdminServiceDep,
) -> list[ConsumptionRecord]:
    return service.list_all_consumption_recors()


@router.get(
    "/admin/batches",
    response_model=list[Batch],
)
async def list_all_batches(
    service: AdminServiceDep,
) -> list[Batch]:
    return service.list_all_batches()
