from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.transaction import TransactionOut
from app.services.idempotency import IdempotencyService, get_idempotency_service
from app.services.transactions import TransactionService, get_transaction_service

router = APIRouter(prefix="/v1/transactions", tags=["transactions"])


@router.post("/seed", response_model=list[TransactionOut])
def seed_transactions(
    service: TransactionService = Depends(get_transaction_service),
    idempotency: IdempotencyService = Depends(get_idempotency_service),
) -> list[TransactionOut]:
    idempotency.clear()
    return [TransactionOut.model_validate(row) for row in service.reset_and_seed()]


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: str,
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionOut:
    row = service.get(transaction_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return TransactionOut.model_validate(row)
