import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False
    )

    type: Mapped[str] = mapped_column(String(20), nullable=False)  # scheduled, repair, inspection, calibration
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    priority: Mapped[str] = mapped_column(String(20), default="normal")  # low, normal, high, urgent

    title: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    scheduled_date: Mapped[Optional[date]] = mapped_column(Date)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    performed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    vendor: Mapped[Optional[str]] = mapped_column(String(200))

    next_maintenance_date: Mapped[Optional[date]] = mapped_column(Date)

    attachments: Mapped[Optional[dict]] = mapped_column(JSONB)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment")
    performer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[performed_by])
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to])
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])


# Import for type hints
from app.models.equipment import Equipment
from app.models.user import User
