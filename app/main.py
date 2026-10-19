from fastapi import FastAPI

from app.api.routes import health, transactions, webhooks

app = FastAPI(title="Walnut")
app.include_router(health.router)
app.include_router(webhooks.router)
app.include_router(transactions.router)
