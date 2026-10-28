from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse, summary="Check application health")
def health() -> HealthResponse:
    """Report process health without checking external dependencies."""

    return HealthResponse(status="ok")
