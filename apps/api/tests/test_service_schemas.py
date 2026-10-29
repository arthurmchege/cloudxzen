import pytest
from pydantic import ValidationError

from app.domains.services.schemas import ServiceCreate


def test_service_create_accepts_valid_values() -> None:
    service = ServiceCreate(
        name="Payments",
        description="Payment processing",
        environment="production",
    )

    assert service.name == "Payments"


@pytest.mark.parametrize("field", ["name", "environment"])
def test_service_create_rejects_blank_required_values(field: str) -> None:
    values = {"name": "Payments", "environment": "production"}
    values[field] = "   "

    with pytest.raises(ValidationError):
        ServiceCreate(**values)


def test_service_create_rejects_overlong_name() -> None:
    with pytest.raises(ValidationError):
        ServiceCreate(name="x" * 201, environment="production")
