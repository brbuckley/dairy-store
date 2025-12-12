from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.config.settings import Settings
from app.domain.admin_service import AdminService
from app.domain.batch_port import BatchPort
from app.domain.batch_service import BatchService
from app.domain.record_port import RecordPort
from app.repositories.batch_repository import BatchRepository
from app.repositories.db_batch_repo import DBBatchRepository
from app.repositories.db_record_repo import DBRecordRepository
from app.repositories.record_repository import RecordRepository


@lru_cache
def get_settings_cached() -> Settings:
    return Settings()


@lru_cache
def get_batch_repo_singleton() -> BatchPort:
    settings = get_settings_cached()
    if settings.env == "dev":
        return BatchRepository()
    if settings.env == "db":
        return DBBatchRepository()
    return BatchRepository()


BatchRepoDep = Annotated[BatchPort, Depends(get_batch_repo_singleton)]


@lru_cache
def get_record_repo_singleton() -> RecordPort:
    settings = get_settings_cached()
    if settings.env == "dev":
        return RecordRepository()
    if settings.env == "db":
        return DBRecordRepository()
    return RecordRepository()


RecordRepoDep = Annotated[RecordPort, Depends(get_record_repo_singleton)]


def get_admin_service(
    batch_repo: BatchRepoDep, record_repo: RecordRepoDep
) -> AdminService:
    return AdminService(batch_repo, record_repo)


AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]


def get_batch_service(
    batch_repo: BatchRepoDep, record_repo: RecordRepoDep
) -> BatchService:
    return BatchService(batch_repo, record_repo)


BatchServiceDep = Annotated[BatchService, Depends(get_batch_service)]
