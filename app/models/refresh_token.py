from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column()

    revoked: Mapped[bool] = mapped_column(default=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    replaced_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("refresh_tokens.id"), default=None)

    device_info: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), default=None)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(default=None)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")