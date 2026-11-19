from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.event import Event
from app.domain.entities.place import Place
from app.domain.repositories.event_repository import EventRepository
from app.infrastructure.models.event import EventModel
from app.infrastructure.models.place import PlaceModel


class PostgreSQLEventRepository(EventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, event_id: UUID) -> Event | None:
        stmt = (
            select(EventModel)
            .options(selectinload(EventModel.place))
            .where(EventModel.id == event_id)
        )

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def create(self, event: Event) -> Event:
        place_model = await self.session.get(
            PlaceModel,
            event.place.id,
        )

        if place_model is None:
            raise ValueError("Place not found")

        model = EventModel(
            id=event.id,
            name=event.name,
            place_id=place_model.id,
            event_time=event.event_time,
            registration_deadline=event.registration_deadline,
            status=event.status,
            number_of_visitors=event.number_of_visitors,
            changed_at=event.changed_at,
            created_at=event.created_at,
            status_changed_at=event.status_changed_at,
        )

        model.place = place_model

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
            .options(selectinload(EventModel.place))
            .order_by(EventModel.event_time)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    @staticmethod
    def _to_entity(model: EventModel) -> Event:
        place = Place(
            id=model.place.id,
            name=model.place.name,
            city=model.place.city,
            address=model.place.address,
            seats_pattern=model.place.seats_pattern,
            changed_at=model.place.changed_at,
            created_at=model.place.created_at,
        )

        return Event(
            id=model.id,
            name=model.name,
            place=place,
            event_time=model.event_time,
            registration_deadline=model.registration_deadline,
            status=model.status,
            number_of_visitors=model.number_of_visitors,
            changed_at=model.changed_at,
            created_at=model.created_at,
            status_changed_at=model.status_changed_at,
        )
