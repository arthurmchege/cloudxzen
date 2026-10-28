"""create service and service event tables

Revision ID: 20260301_0001
Revises:
Create Date: 2026-03-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260301_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("environment", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "service_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("event_type IN ('check', 'incident')", name="ck_service_events_event_type"),
        sa.CheckConstraint("status IN ('operational', 'degraded', 'down')", name="ck_service_events_status"),
        sa.CheckConstraint("(event_type = 'check') OR status IN ('degraded', 'down')", name="ck_service_events_incident_status"),
        sa.CheckConstraint("length(btrim(summary)) > 0", name="ck_service_events_summary_not_blank"),
        sa.CheckConstraint("(event_type = 'check' AND resolved_at IS NULL) OR (event_type = 'incident')", name="ck_service_events_check_not_resolved"),
        sa.CheckConstraint("resolved_at IS NULL OR resolved_at >= occurred_at", name="ck_service_events_resolution_after_occurrence"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_events_service_occurred", "service_events", ["service_id", "occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_service_events_service_occurred", table_name="service_events")
    op.drop_table("service_events")
    op.drop_table("services")
