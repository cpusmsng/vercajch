import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Date, Text, Integer, Numeric, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20))
    parent_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id")
    )

    default_maintenance_interval_days: Mapped[Optional[int]] = mapped_column(Integer)
    requires_certification: Mapped[bool] = mapped_column(Boolean, default=False)
    transfer_requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    max_transfer_days: Mapped[Optional[int]] = mapped_column(Integer)

    icon: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(7))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent")
    equipment: Mapped[List["Equipment"]] = relationship("Equipment", back_populates="category")
    models: Mapped[List["EquipmentModel"]] = relationship("EquipmentModel", back_populates="category")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # warehouse, project, vehicle, other
    code: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    gps_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8))
    gps_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8))

    parent_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id")
    )
    responsible_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    parent: Mapped[Optional["Location"]] = relationship("Location", remote_side=[id], back_populates="children")
    children: Mapped[List["Location"]] = relationship("Location", back_populates="parent")
    responsible_user: Mapped[Optional["User"]] = relationship("User")
    equipment: Mapped[List["Equipment"]] = relationship(
        "Equipment", back_populates="current_location", foreign_keys="Equipment.current_location_id"
    )


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255))
    support_email: Mapped[Optional[str]] = mapped_column(String(255))
    support_phone: Mapped[Optional[str]] = mapped_column(String(50))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    models: Mapped[List["EquipmentModel"]] = relationship("EquipmentModel", back_populates="manufacturer")


class EquipmentModel(Base):
    __tablename__ = "equipment_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manufacturer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("manufacturers.id")
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    default_calibration_interval_days: Mapped[Optional[int]] = mapped_column(Integer)
    requires_calibration: Mapped[bool] = mapped_column(Boolean, default=False)
    manual_url: Mapped[Optional[str]] = mapped_column(String(500))
    specifications: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    manufacturer: Mapped[Optional["Manufacturer"]] = relationship("Manufacturer", back_populates="models")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="models")
    equipment: Mapped[List["Equipment"]] = relationship("Equipment", back_populates="model")


class AccessoryType(Base):
    __tablename__ = "accessory_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    default_for_categories: Mapped[Optional[List[uuid.UUID]]] = mapped_column(ARRAY(UUID(as_uuid=True)))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"))
    model_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment_models.id"))
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))
    internal_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    model_name: Mapped[Optional[str]] = mapped_column(String(100))

    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    current_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    warranty_expiry: Mapped[Optional[date]] = mapped_column(Date)

    condition: Mapped[str] = mapped_column(String(20), default="good")  # new, good, fair, poor, broken
    status: Mapped[str] = mapped_column(String(20), default="available")  # available, checked_out, maintenance, retired

    photo_url: Mapped[Optional[str]] = mapped_column(String(500))

    current_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id")
    )
    current_holder_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    home_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("locations.id"))

    # Accessories
    is_main_item: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_equipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id")
    )
    is_transferable: Mapped[bool] = mapped_column(Boolean, default=True)
    transfer_requires_approval: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Calibration
    requires_calibration: Mapped[bool] = mapped_column(Boolean, default=False)
    calibration_interval_days: Mapped[Optional[int]] = mapped_column(Integer)
    last_calibration_date: Mapped[Optional[date]] = mapped_column(Date)
    next_calibration_date: Mapped[Optional[date]] = mapped_column(Date)
    calibration_status: Mapped[Optional[str]] = mapped_column(String(20))  # valid, expiring, expired, not_required

    # Maintenance
    next_maintenance_date: Mapped[Optional[date]] = mapped_column(Date)
    last_maintenance_date: Mapped[Optional[date]] = mapped_column(Date)

    notes: Mapped[Optional[str]] = mapped_column(Text)
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="equipment")
    model: Mapped[Optional["EquipmentModel"]] = relationship("EquipmentModel", back_populates="equipment")
    current_location: Mapped[Optional["Location"]] = relationship(
        "Location", back_populates="equipment", foreign_keys=[current_location_id]
    )
    home_location: Mapped[Optional["Location"]] = relationship("Location", foreign_keys=[home_location_id])
    current_holder: Mapped[Optional["User"]] = relationship("User", back_populates="held_equipment")

    parent_equipment: Mapped[Optional["Equipment"]] = relationship(
        "Equipment", remote_side=[id], back_populates="accessories"
    )
    accessories: Mapped[List["Equipment"]] = relationship("Equipment", back_populates="parent_equipment")

    tags: Mapped[List["EquipmentTag"]] = relationship("EquipmentTag", back_populates="equipment")
    photos: Mapped[List["EquipmentPhoto"]] = relationship("EquipmentPhoto", back_populates="equipment")
    calibrations: Mapped[List["Calibration"]] = relationship("Calibration", back_populates="equipment")
    checkouts: Mapped[List["Checkout"]] = relationship("Checkout", back_populates="equipment")

    def __repr__(self):
        return f"<Equipment {self.name} ({self.internal_code})>"


class EquipmentTag(Base):
    __tablename__ = "equipment_tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id"))

    tag_type: Mapped[str] = mapped_column(String(20), nullable=False)  # qr_code, rfid_nfc, rfid_uhf, barcode
    tag_value: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    rfid_uid: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    rfid_technology: Mapped[Optional[str]] = mapped_column(String(50))

    status: Mapped[str] = mapped_column(String(20), default="active")  # active, damaged, lost, replaced

    printed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_scanned_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    scan_count: Mapped[int] = mapped_column(Integer, default=0)

    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment: Mapped[Optional["Equipment"]] = relationship("Equipment", back_populates="tags")
    creator: Mapped[Optional["User"]] = relationship("User")


class EquipmentPhoto(Base):
    __tablename__ = "equipment_photos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False
    )

    photo_type: Mapped[str] = mapped_column(String(20), nullable=False)  # main, detail, label, damage, calibration
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))

    local_path: Mapped[Optional[str]] = mapped_column(String(500))
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    sync_error: Mapped[Optional[str]] = mapped_column(Text)

    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)

    description: Mapped[Optional[str]] = mapped_column(Text)
    taken_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="photos")
    uploader: Mapped[Optional["User"]] = relationship("User")


# Import for type hints
from app.models.user import User
from app.models.calibration import Calibration
from app.models.checkout import Checkout
