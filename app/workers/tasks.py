import time

from app.config import get_settings
from app.core.supabase_client import get_supabase
from app.services.transactions import TransactionService
from app.workers.celery_app import celery_app


@celery_app.task(name="process_transaction")
def process_transaction(transaction_id: str) -> None:
    time.sleep(get_settings().processing_delay_seconds)
    TransactionService(get_supabase()).mark_processed(transaction_id)
