from redis import Redis

from app.core.redis_client import get_redis

PREFIX = "idempotency:"
LOCKED = "1"


class IdempotencyService:
    def __init__(self, client: Redis | None = None) -> None:
        self._client = client

    def _redis(self) -> Redis:
        if self._client is None:
            self._client = get_redis()
        return self._client

    def _key(self, transaction_id: str) -> str:
        return f"{PREFIX}{transaction_id}"

    def reserve(self, transaction_id: str) -> bool:
        created = self._redis().set(self._key(transaction_id), LOCKED, nx=True)
        return bool(created)

    def release(self, transaction_id: str) -> None:
        self._redis().delete(self._key(transaction_id))

    def clear(self) -> None:
        client = self._redis()
        keys = list(client.scan_iter(match=f"{PREFIX}*"))
        if keys:
            client.delete(*keys)


def get_idempotency_service() -> IdempotencyService:
    return IdempotencyService()
