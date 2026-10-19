from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.transaction import HealthOut

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthOut)
def health() -> HealthOut:
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return HealthOut(status="HEALTHY", current_time=current_time)
