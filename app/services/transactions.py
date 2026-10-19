from datetime import datetime, timezone

from supabase import Client

from app.core.supabase_client import get_supabase
from app.data.seed import seed_rows
from app.schemas.transaction import PENDING, PROCESSED, PROCESSING

TABLE = "transactions"


class TransactionService:
    def __init__(self, client: Client | None = None) -> None:
        self._client = client

    def _query(self):
        if self._client is None:
            self._client = get_supabase()
        return self._client.table(TABLE)

    def get(self, transaction_id: str) -> dict | None:
        result = (
            self._query()
            .select("*")
            .eq("transaction_id", transaction_id)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        return rows[0] if rows else None

    def mark_processing(self, transaction_id: str) -> None:
        (
            self._query()
            .update({"status": PROCESSING})
            .eq("transaction_id", transaction_id)
            .execute()
        )

    def mark_pending(self, transaction_id: str) -> None:
        (
            self._query()
            .update({"status": PENDING})
            .eq("transaction_id", transaction_id)
            .eq("status", PROCESSING)
            .execute()
        )

    def mark_processed(self, transaction_id: str) -> None:
        processed_at = datetime.now(timezone.utc).isoformat()
        (
            self._query()
            .update({"status": PROCESSED, "processed_at": processed_at})
            .eq("transaction_id", transaction_id)
            .eq("status", PROCESSING)
            .execute()
        )

    def reset_and_seed(self) -> list[dict]:
        self._query().delete().neq("transaction_id", "").execute()
        result = self._query().insert(seed_rows(), default_to_null=False).execute()
        return result.data or []


def get_transaction_service() -> TransactionService:
    return TransactionService()
