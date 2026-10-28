from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EventType(StrEnum):
    CHECK = "check"
    INCIDENT = "incident"


class ServiceStatus(StrEnum):
    UNKNOWN = "unknown"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"


class ServiceEventStatus(StrEnum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    environment: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    events: Mapped[list[ServiceEvent]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ServiceEvent(Base):
    __tablename__ = "service_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('check', 'incident')",
            name="ck_service_events_event_type",
        ),
        CheckConstraint(
            "status IN ('operational', 'degraded', 'down')",
            name="ck_service_events_status",
        ),
        CheckConstraint(
            "(event_type = 'check') OR status IN ('degraded', 'down')",
            name="ck_service_events_incident_status",
        ),
        CheckConstraint(
            "length(btrim(summary)) > 0",
            name="ck_service_events_summary_not_blank",
        ),
        CheckConstraint(
            "(event_type = 'check' AND resolved_at IS NULL) OR "
            "(event_type = 'incident')",
            name="ck_service_events_check_not_resolved",
        ),
        CheckConstraint(
            "resolved_at IS NULL OR resolved_at >= occurred_at",
            name="ck_service_events_resolution_after_occurrence",
        ),
        Index("ix_service_events_service_occurred", "service_id", "occurred_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    service_id: Mapped[UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[EventType] = mapped_column(String(16), nullable=False)
    status: Mapped[ServiceEventStatus] = mapped_column(String(16), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    service: Mapped[Service] = relationship(back_populates="events")
