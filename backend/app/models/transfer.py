import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class TransferRequest(Base):
    __tablename__ = "transfer_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    request_type: Mapped[str] = mapped_column(String(20), nullable=False)  # direct, broadcast, offer

    equipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id"))
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"))

    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    holder_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("locations.id"))
    location_note: Mapped[Optional[str]] = mapped_column(String(200))

    needed_from: Mapped[Optional[datetime]] = mapped_column(DateTime)
    needed_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    message: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default="pending")
    # pending, accepted, rejected, cancelled, expired, completed, requires_approval

    requires_leader_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    equipment: Mapped[Optional["Equipment"]] = relationship("Equipment")
    category: Mapped[Optional["Category"]] = relationship("Category")
    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id])
    holder: Mapped[Optional["User"]] = relationship("User", foreign_keys=[holder_id])
    location: Mapped[Optional["Location"]] = relationship("Location")
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    offers: Mapped[List["TransferOffer"]] = relationship("TransferOffer", back_populates="request")


class TransferOffer(Base):
    __tablename__ = "transfer_offers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transfer_requests.id", ondelete="CASCADE")
    )

    offerer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False
    )

    message: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, accepted, rejected

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    request: Mapped["TransferRequest"] = relationship("TransferRequest", back_populates="offers")
    offerer: Mapped["User"] = relationship("User")
    equipment: Mapped["Equipment"] = relationship("Equipment")


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False
    )
    request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transfer_requests.id")
    )

    from_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("locations.id"))
    transfer_gps_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8))
    transfer_gps_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8))

    from_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    to_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    condition_at_transfer: Mapped[Optional[str]] = mapped_column(String(20))
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    transfer_type: Mapped[str] = mapped_column(String(20), default="peer")  # peer, checkout, checkin, handover

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment")
    request: Mapped[Optional["TransferRequest"]] = relationship("TransferRequest")
    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id])
    to_user: Mapped["User"] = relationship("User", foreign_keys=[to_user_id])
    location: Mapped[Optional["Location"]] = relationship("Location")


# Import for type hints
from app.models.equipment import Equipment, Category, Location
from app.models.user import User
