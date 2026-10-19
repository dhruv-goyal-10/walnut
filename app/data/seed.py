from app.schemas.transaction import PENDING

SEED_TRANSACTIONS: list[dict] = [
    {
        "transaction_id": "txn_abc123def456",
        "source_account": "acc_user_789",
        "destination_account": "acc_merchant_456",
        "amount": 1500,
        "currency": "INR",
        "status": PENDING,
    },
    {
        "transaction_id": "txn_usd_1001",
        "source_account": "acc_user_001",
        "destination_account": "acc_merchant_010",
        "amount": 150.50,
        "currency": "USD",
        "status": PENDING,
    },
    {
        "transaction_id": "txn_eur_2002",
        "source_account": "acc_user_002",
        "destination_account": "acc_merchant_020",
        "amount": 89.99,
        "currency": "EUR",
        "status": PENDING,
    },
    {
        "transaction_id": "txn_inr_3003",
        "source_account": "acc_user_003",
        "destination_account": "acc_merchant_030",
        "amount": 2500,
        "currency": "INR",
        "status": PENDING,
    },
]


def seed_rows() -> list[dict]:
    return [dict(row) for row in SEED_TRANSACTIONS]
