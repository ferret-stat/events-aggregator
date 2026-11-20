from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import EventStatus
from app.infrastructure.database import Base
from app.infrastructure.models.place import PlaceModel


class EventModel(Base):
    __tablename__ = "events"

    __table_args__ = (
        Index("ix_events_changed_at", "changed_at"),
        Index("ix_events_event_time", "event_time"),
        Index("ix_events_status_event_time", "status", "event_time"),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    place_id: Mapped[UUID] = mapped_column(
        ForeignKey("places.id", ondelete="RESTRICT"),
        nullable=False,
    )

    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[EventStatus] = mapped_column(
        SQLAlchemyEnum(
            EventStatus,
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            length=50,
        ),
        nullable=False,
    )

    number_of_visitors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    place: Mapped["PlaceModel"] = relationship(
        "PlaceModel",
        back_populates="events",
    )
