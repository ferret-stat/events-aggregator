from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.event import Event
from app.domain.repositories.event_repository import EventRepository
from app.infrastructure.models.event import EventModel


class PostgreSQLEventRepository(EventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: UUID) -> Event | None:
        stmt = select(EventModel).where(EventModel.id == event_id)

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def create(self, event: Event) -> Event:
        model = EventModel(
            id=event.id,
            title=event.title,
            description=event.description,
            event_time=event.event_time,
            place_id=event.place_id,
            status=event.status,
        )

        self.session.add(model)
        await self.session.flush()

        return self._to_entity(model)

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Event]:
        stmt = (
            select(EventModel)
            .order_by(EventModel.event_time)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    @staticmethod
    def _to_entity(model: EventModel) -> Event:
        return Event(
            id=model.id,
            title=model.title,
            description=model.description,
            event_time=model.event_time,
            place_id=model.place_id,
            status=model.status,
        )
