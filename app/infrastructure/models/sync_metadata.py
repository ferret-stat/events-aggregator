from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import SyncStatus
from app.infrastructure.database import Base


class SyncMetadataModel(Base):
    __tablename__ = "sync_metadata"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
    )

    last_sync_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    sync_status: Mapped[SyncStatus] = mapped_column(
        SQLAlchemyEnum(
            SyncStatus,
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            length=20,
        ),
        nullable=False,
        default=SyncStatus.NEVER_SYNCED,
    )

    last_error: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
