from locust import HttpUser, task

BASE_URL = "http://127.0.0.1:8000"
BATCH_ID = 2
CONCURRENT = 500
QTY = 0.25


class BatchUser(HttpUser):
    host = BASE_URL

    @task
    def read_batch(self):
        old_batch = self.client.get(f"/api/batches/{BATCH_ID}").json()
        consume_payload = {
            "qty": QTY,
            "order_id": "ORDER-20251204-1234",
        }
        self.client.post(
            f"/api/batches/{BATCH_ID}/consume", json=consume_payload
        )
        new_batch = self.client.get(f"/api/batches/{BATCH_ID}").json()
        assert new_batch["volume_liters"] == old_batch["volume_liters"] - QTY
