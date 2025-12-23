import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Date, Text, Integer, Numeric, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class Calibration(Base):
    __tablename__ = "calibrations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False
    )

    calibration_type: Mapped[str] = mapped_column(String(20), nullable=False)  # initial, periodic, after_repair, verification
    calibration_date: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    next_calibration_date: Mapped[Optional[date]] = mapped_column(Date)

    performed_by_type: Mapped[Optional[str]] = mapped_column(String(20))  # internal, external, manufacturer
    performed_by_name: Mapped[Optional[str]] = mapped_column(String(200))
    calibration_lab: Mapped[Optional[str]] = mapped_column(String(200))

    certificate_number: Mapped[Optional[str]] = mapped_column(String(100))
    certificate_url: Mapped[Optional[str]] = mapped_column(String(500))

    result: Mapped[str] = mapped_column(String(20), nullable=False)  # passed, passed_with_adjustment, failed
    notes: Mapped[Optional[str]] = mapped_column(Text)

    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    cost_currency: Mapped[str] = mapped_column(String(3), default="EUR")

    attachments: Mapped[Optional[dict]] = mapped_column(JSONB)

    recorded_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="calibrations")
    recorder: Mapped[Optional["User"]] = relationship("User")


class CalibrationReminderSetting(Base):
    __tablename__ = "calibration_reminder_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    scope_type: Mapped[str] = mapped_column(String(20), nullable=False)  # global, category, equipment
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"))
    equipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id"))

    days_before: Mapped[List[int]] = mapped_column(ARRAY(Integer), default=[30, 14, 7, 1])

    notify_holder: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_manager: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_users: Mapped[Optional[List[uuid.UUID]]] = mapped_column(ARRAY(UUID(as_uuid=True)))

    notify_push: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_in_app: Mapped[bool] = mapped_column(Boolean, default=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category")
    equipment: Mapped[Optional["Equipment"]] = relationship("Equipment")
    creator: Mapped[Optional["User"]] = relationship("User")


class CalibrationReminderSent(Base):
    __tablename__ = "calibration_reminders_sent"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False
    )
    calibration_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("calibrations.id")
    )

    reminder_type: Mapped[Optional[str]] = mapped_column(String(20))  # 30_days, 14_days, 7_days, 1_day, expired
    sent_to: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    sent_via: Mapped[Optional[str]] = mapped_column(String(20))  # push, email, in_app

    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# Import for type hints
from app.models.equipment import Equipment, Category
from app.models.user import User
