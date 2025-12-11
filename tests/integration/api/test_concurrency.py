import asyncio

import httpx
import pytest
from fastapi import status

BASE_URL = "http://127.0.0.1:8000"
BATCH_ID = 2
CONCURRENT = 500
QTY = 0.25


async def _consume(client: httpx.AsyncClient, batch_id: int, qty: float):
    resp = await client.post(
        f"{BASE_URL}/api/batches/{batch_id}/consume",
        json={"qty": qty, "order_id": "ORDER-20251204-1234"},
    )
    return (
        resp.status_code,
        resp.json()
        if resp.status_code == status.HTTP_200_OK
        else await resp.aread(),
    )


@pytest.mark.asyncio
async def test_concurrent_consume_httpx():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # read initial
        r = await client.get(f"{BASE_URL}/api/batches/{BATCH_ID}")
        assert r.status_code == status.HTTP_200_OK
        initial_volume = r.json()["volume_liters"]

        tasks = [
            asyncio.create_task(_consume(client, BATCH_ID, QTY))
            for _ in range(CONCURRENT)
        ]
        await asyncio.gather(*tasks)

        # read final volume
        r2 = await client.get(f"{BASE_URL}/api/batches/{BATCH_ID}")
        assert r2.status_code == status.HTTP_200_OK
        final_volume = r2.json()["volume_liters"]

        assert final_volume == initial_volume - (CONCURRENT * QTY)
