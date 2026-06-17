import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id: Mapped[str] = mapped_column(
        String, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    source_file: Mapped[str] = mapped_column(String, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    excerpt: Mapped[str | None] = mapped_column(String, nullable=True)
    chunk_id: Mapped[str | None] = mapped_column(String, nullable=True)

    message: Mapped["Message"] = relationship("Message", back_populates="citations")  # noqa: F821
