import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Checkout(Base):
    __tablename__ = "checkouts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("locations.id"))

    checkout_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expected_return_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_return_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    checkout_condition: Mapped[Optional[str]] = mapped_column(String(20))
    checkout_photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    checkout_notes: Mapped[Optional[str]] = mapped_column(Text)
    checkout_gps_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8))
    checkout_gps_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8))

    return_condition: Mapped[Optional[str]] = mapped_column(String(20))
    return_photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    return_notes: Mapped[Optional[str]] = mapped_column(Text)
    return_gps_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8))
    return_gps_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8))

    checked_out_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    checked_in_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    status: Mapped[str] = mapped_column(String(20), default="active")  # active, returned, overdue

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="checkouts")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    location: Mapped[Optional["Location"]] = relationship("Location")
    checkout_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[checked_out_by])
    checkin_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[checked_in_by])


# Import for type hints
from app.models.equipment import Equipment, Location
from app.models.user import User
