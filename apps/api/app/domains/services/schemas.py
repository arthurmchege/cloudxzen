from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domains.services.models import EventType, ServiceEventStatus, ServiceStatus


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    environment: str = Field(min_length=1, max_length=32)

    @field_validator("name", "environment")
    @classmethod
    def reject_blank_values(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    environment: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    created_at: datetime
    updated_at: datetime


class ServiceEventCreate(BaseModel):
    event_type: EventType
    status: ServiceEventStatus
    summary: str = Field(min_length=1, max_length=500)
    details: str | None = None
    occurred_at: datetime

    @field_validator("summary")
    @classmethod
    def reject_blank_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("occurred_at")
    @classmethod
    def require_timezone_aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("must include timezone information")
        return value

    @model_validator(mode="after")
    def validate_event_status(self) -> ServiceEventCreate:
        if (
            self.event_type is EventType.INCIDENT
            and self.status is ServiceEventStatus.OPERATIONAL
        ):
            raise ValueError("incident events cannot have operational status")
        return self


class ServiceEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_id: UUID
    event_type: EventType
    status: ServiceEventStatus
    summary: str
    details: str | None
    occurred_at: datetime
    resolved_at: datetime | None
    created_at: datetime

    @model_validator(mode="after")
    def validate_resolution(self) -> ServiceEventResponse:
        if self.resolved_at is not None and self.resolved_at < self.occurred_at:
            raise ValueError("resolved_at must not precede occurred_at")
        return self
