from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.transaction import WebhookAck, WebhookIn
from app.services.idempotency import IdempotencyService, get_idempotency_service
from app.services.transactions import TransactionService, get_transaction_service
from app.workers.tasks import process_transaction

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])


@router.post(
    "/transactions",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=WebhookAck,
)
def receive_transaction_webhook(
    payload: WebhookIn,
    service: TransactionService = Depends(get_transaction_service),
    idempotency: IdempotencyService = Depends(get_idempotency_service),
) -> WebhookAck:
    if service.get(payload.transaction_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    if not idempotency.reserve(payload.transaction_id):
        return WebhookAck(transaction_id=payload.transaction_id)

    try:
        service.mark_processing(payload.transaction_id)
        process_transaction.delay(payload.transaction_id)
    except Exception:
        idempotency.release(payload.transaction_id)
        service.mark_pending(payload.transaction_id)
        raise
    return WebhookAck(transaction_id=payload.transaction_id)
