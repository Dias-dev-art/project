from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True)
    repo_full_name: Mapped[str] = mapped_column(String(255), index=True)
    pr_number: Mapped[int] = mapped_column(Integer)
    head_sha: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    findings: Mapped[list["Finding"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), index=True)
    rule_id: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(20))
    file_path: Mapped[str] = mapped_column(String(500))
    line: Mapped[int | None] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)  # Claude-generated

    scan: Mapped[Scan] = relationship(back_populates="findings")
