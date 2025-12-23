import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    entity_type: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), index=True)

    old_values: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_values: Mapped[Optional[dict]] = mapped_column(JSONB)

    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 compatible
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    platform: Mapped[Optional[str]] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")


# Import for type hints
from app.models.user import User
