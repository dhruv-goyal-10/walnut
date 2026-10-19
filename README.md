# Walnut

Transaction webhook service. It acknowledges payment-processor webhooks immediately, then finishes each transaction in the background.

A transaction moves through three states:

`PENDING` → `PROCESSING` → `PROCESSED`

Seeded rows start as `PENDING`. A webhook for that id moves the row to `PROCESSING` and queues the work. About 30 seconds later the worker marks it `PROCESSED`.

## Stack

- FastAPI
- Supabase (Postgres via `supabase-py`)
- Redis + Celery
- Docker Compose (`api`, `worker`, `redis`)

## Endpoints

| Method | Path | Behavior |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/v1/transactions/seed` | Deletes every row, inserts the dummy `PENDING` transactions, returns them |
| `POST` | `/v1/webhooks/transactions` | `202` in well under 500ms |
| `GET` | `/v1/transactions/{transaction_id}` | Transaction object, or `404` |

Webhook body:

```json
{
  "transaction_id": "txn_abc123def456",
  "source_account": "acc_user_789",
  "destination_account": "acc_merchant_456",
  "amount": 1500,
  "currency": "INR"
}
```

Invalid JSON or missing fields returns `422`. An unknown `transaction_id` returns `404` and is not cached. A second webhook for an id already reserved in Redis returns `202` and does not run the work again.

## Idempotency

Redis is only the lock. The key is `idempotency:{transaction_id}`; the value is a fixed token and carries no status. Status lives in Supabase.

1. The transaction must already exist in Supabase. If it does not, the API returns `404` and writes nothing to Redis.
2. `SET key 1 NX` reserves the id. Only the first caller gets the key.
3. That caller sets the Supabase row to `PROCESSING` and enqueues the worker.
4. After the 30 second delay the worker sets the Supabase row to `PROCESSED`. The Redis key stays put so a later webhook is still a no-op.
5. If the queue rejects the task, the API deletes the Redis key and sets the row back to `PENDING`.

Seeding clears every `idempotency:*` key, then replaces the table.

## 1. Create the Supabase table

In the Supabase SQL editor, run:

```sql
create table if not exists transactions (
    transaction_id text primary key,
    source_account text not null,
    destination_account text not null,
    amount numeric not null,
    currency text not null,
    status text not null default 'PENDING',
    created_at timestamptz not null default now(),
    processed_at timestamptz,
    constraint transactions_status_check
        check (status in ('PENDING', 'PROCESSING', 'PROCESSED'))
);
```

Use the **secret** key (`sb_secret_...`) from Project Settings → API Keys in `.env`. The publishable key (`sb_publishable_...`) is blocked by row-level security; the secret key is not. Legacy JWT `service_role` keys still work if your project still shows them.

## 2. Configure environment

```bash
cp .env.example .env
```

Set `SUPABASE_URL` and `SUPABASE_KEY`. Leave `PROCESSING_DELAY_SECONDS=30`.

`REDIS_URL` defaults to `redis://localhost:6379/0` for a local process. Docker Compose overrides it to `redis://redis:6379/0` for the `api` and `worker` containers.

## 3. Run with Docker (Oracle VM)

From the project root:

```bash
docker compose up -d --build
```

The API listens on port `8000`. Redis is published on `6379` so a local process can use the same broker.

```bash
docker compose logs -f api worker
docker compose down
```

To add worker processes later, without any other change:

```bash
docker compose up -d --scale worker=3
```

## 4. Run locally with a virtualenv

Requires Python 3.12+ and a reachable Redis (the Compose Redis service is enough).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d redis

uvicorn app.main:app --reload --port 8000
```

In a second terminal, with the same virtualenv:

```bash
source .venv/bin/activate
celery -A app.workers.celery_app:celery_app worker --loglevel=info
```

## 5. Exercise the flow

```bash
curl -s http://localhost:8000/

curl -s -X POST http://localhost:8000/v1/transactions/seed

curl -s -X POST http://localhost:8000/v1/webhooks/transactions \
  -H 'Content-Type: application/json' \
  -d '{
    "transaction_id": "txn_abc123def456",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR"
  }'

curl -s http://localhost:8000/v1/transactions/txn_abc123def456
```

Right after the webhook the status is `PROCESSING` and `processed_at` is `null`. About 30 seconds later it is `PROCESSED` with `processed_at` set. Sending that webhook again returns `202` and does not create a second row.

`POST /v1/transactions/seed` wipes the table. Use it only to reset the test data.
