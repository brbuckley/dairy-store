# app/config/dependency_injection.py
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.config.settings import Settings
from app.domain.batch_port import BatchPort
from app.domain.batch_service import BatchService
from app.repositories.batch_repository import BatchRepository


@lru_cache
def get_settings_cached() -> Settings:
    return Settings()


@lru_cache
def get_batch_repo_singleton() -> BatchPort:
    settings = get_settings_cached()
    if settings.env == "dev":
        return BatchRepository()
    return BatchRepository()


# Use Annotated for the dependency instead of calling Depends() in the default arg
BatchRepoDep = Annotated[BatchPort, Depends(get_batch_repo_singleton)]


def get_batch_service(repo: BatchRepoDep) -> BatchService:
    return BatchService(repo)


BatchServiceDep = Annotated[BatchService, Depends(get_batch_service)]
