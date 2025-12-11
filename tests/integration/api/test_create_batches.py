from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient

from app.__main__ import app

client = TestClient(app)
now = datetime.now(UTC)
now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_create_batch_returns_created_batch():
    # Arrange
    payload = {
        "batch_code": "SCH-20251204-0001",
        "received_at": now_str,
        "shelf_life_days": 7,
        "volume_liters": 1000.0,
        "fat_percent": 3.5,
    }

    # Act
    response = client.post("/api/batches", json=payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED, response.text

    body = response.json()

    # ID must be present and auto-generated
    assert "id" in body
    assert isinstance(body["id"], int)
    assert body["id"] > 0

    # All other fields should match the request payload exactly
    assert body["batch_code"] == payload["batch_code"]
    assert body["received_at"] == payload["received_at"]
    assert body["shelf_life_days"] == payload["shelf_life_days"]
    assert body["volume_liters"] == payload["volume_liters"]
    assert body["fat_percent"] == payload["fat_percent"]


def test_read_all_batches_returns_batches():
    # Act
    response = client.get("/api/batches")

    # Assert
    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()

    assert isinstance(body, list)
    assert len(body) > 0

    for batch in body:
        assert batch["id"] is not None


def test_read_by_id_returns_batch():
    # First make sure the batch exists (id = 1) – or you can create one explicitly.
    create_payload = {
        "batch_code": "SCH-20251204-0002",
        "received_at": now_str,
        "shelf_life_days": 7,
        "volume_liters": 500.0,
        "fat_percent": 3.2,
    }
    create_response = client.post("/api/batches", json=create_payload)
    assert create_response.status_code == status.HTTP_201_CREATED, (
        create_response.text
    )
    created_batch = create_response.json()
    batch_id = created_batch["id"]

    # Act
    response = client.get(f"/api/batches/{batch_id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()

    assert body["id"] == batch_id


def test_consume_batch_reduces_volume_and_returns_updated_batch():
    # Arrange: create a new batch to consume from
    create_payload = {
        "batch_code": "SCH-20251204-0002",
        "received_at": now_str,
        "shelf_life_days": 7,
        "volume_liters": 500.0,
        "fat_percent": 3.2,
    }
    create_response = client.post("/api/batches", json=create_payload)
    assert create_response.status_code == status.HTTP_201_CREATED, (
        create_response.text
    )
    created_batch = create_response.json()
    batch_id = created_batch["id"]

    consume_payload = {
        "qty": 100.5,
        "order_id": "ORD-12345",
    }

    # Act
    client.post(f"/api/batches/{batch_id}/consume", json=consume_payload)
    response = client.get(f"/api/batches/{batch_id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()

    assert body["id"] == batch_id
    # Assuming business logic: new volume = old volume - qty
    assert (
        body["volume_liters"]
        == create_payload["volume_liters"] - consume_payload["qty"]
    )
    # Other fields should remain unchanged
    assert body["batch_code"] == create_payload["batch_code"]
    assert body["received_at"] == create_payload["received_at"]
    assert body["shelf_life_days"] == create_payload["shelf_life_days"]
    assert body["fat_percent"] == create_payload["fat_percent"]


def test_near_expiry_returns_batches():
    # Act
    create_payload = {
        "batch_code": "SCH-20251204-0002",
        "received_at": now_str,
        "shelf_life_days": 1,
        "volume_liters": 500.0,
        "fat_percent": 3.2,
    }
    create_response = client.post("/api/batches", json=create_payload)
    assert create_response.status_code == status.HTTP_201_CREATED, (
        create_response.text
    )
    n_days = 3
    response = client.get(
        url="/api/batches/near-expiry", params={"n_days": n_days}
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()

    assert isinstance(body, list)
    # At least we verify the shape; domain rules can be tightened later
    for batch in body:
        expiry = datetime.fromisoformat(batch["received_at"]) + timedelta(
            days=batch["shelf_life_days"]
        )
        assert batch["id"] is not None
        assert now <= expiry
        assert expiry <= now + timedelta(days=n_days)


def test_delete_batch_soft_deletes_and_returns_204():
    # Arrange: create a batch to delete
    create_payload = {
        "batch_code": "SCH-20251204-0003",
        "received_at": now_str,
        "shelf_life_days": 7,
        "volume_liters": 200.0,
        "fat_percent": 3.8,
    }
    create_response = client.post("/api/batches", json=create_payload)
    assert create_response.status_code == status.HTTP_201_CREATED, (
        create_response.text
    )
    created_batch = create_response.json()
    batch_id = created_batch["id"]

    # Act: delete the batch
    delete_response = client.delete(f"/api/batches/{batch_id}")

    # Assert
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT, (
        delete_response.text
    )
    assert delete_response.content in (b"", None)

    # Optional: verify it no longer appears / returns 404
    get_response = client.get(f"/api/batches/{batch_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    # Adjust this expectation based on how you want soft-delete to behave:
    # either 404 Not Found or status.HTTP_200_OK but flagged as deleted.
    # For stricter behavior, uncomment the next line if your service ra
