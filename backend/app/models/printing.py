import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Text, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Printer(Base):
    __tablename__ = "printers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # zebra_zpl, brother_ql, dymo, generic_escpos

    connection_type: Mapped[Optional[str]] = mapped_column(String(20))  # usb, bluetooth, network
    connection_address: Mapped[Optional[str]] = mapped_column(String(255))

    dpi: Mapped[int] = mapped_column(Integer, default=203)
    default_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LabelTemplate(Base):
    __tablename__ = "label_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    width_mm: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    height_mm: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    template_type: Mapped[Optional[str]] = mapped_column(String(20))  # zpl, escpos, json
    template_content: Mapped[Optional[str]] = mapped_column(Text)

    includes_qr: Mapped[bool] = mapped_column(Boolean, default=True)
    includes_barcode: Mapped[bool] = mapped_column(Boolean, default=False)
    includes_name: Mapped[bool] = mapped_column(Boolean, default=True)
    includes_serial: Mapped[bool] = mapped_column(Boolean, default=True)
    includes_category: Mapped[bool] = mapped_column(Boolean, default=False)
    includes_logo: Mapped[bool] = mapped_column(Boolean, default=False)

    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PrintJob(Base):
    __tablename__ = "print_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    printer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("printers.id"))
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("label_templates.id")
    )

    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, printing, completed, failed

    total_count: Mapped[Optional[int]] = mapped_column(Integer)
    printed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)

    error_message: Mapped[Optional[str]] = mapped_column(Text)

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    printer: Mapped[Optional["Printer"]] = relationship("Printer")
    template: Mapped[Optional["LabelTemplate"]] = relationship("LabelTemplate")
    creator: Mapped[Optional["User"]] = relationship("User")
    items: Mapped[List["PrintJobItem"]] = relationship("PrintJobItem", back_populates="print_job")


class PrintJobItem(Base):
    __tablename__ = "print_job_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    print_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("print_jobs.id", ondelete="CASCADE")
    )
    equipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment.id"))
    tag_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("equipment_tags.id"))

    status: Mapped[str] = mapped_column(String(20), default="pending")
    printed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    print_job: Mapped["PrintJob"] = relationship("PrintJob", back_populates="items")
    equipment: Mapped[Optional["Equipment"]] = relationship("Equipment")
    tag: Mapped[Optional["EquipmentTag"]] = relationship("EquipmentTag")


# Import for type hints
from app.models.equipment import Equipment, EquipmentTag
from app.models.user import User
