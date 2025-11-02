from typing import Generic, TypeVar

from pydantic import Field
from pydantic.dataclasses import dataclass

from domain.events import DomainEvent
from domain.value_objects import GenericUUID

EntityId = TypeVar("EntityId", bound=GenericUUID)


@dataclass
class Entity(Generic[EntityId]):
    """A base class for all entities"""

    id: EntityId = Field(
        default_factory=lambda: GenericUUID.next_id(), kw_only=True, hash=True
    )


@dataclass(kw_only=True)
class AggregateRoot(Entity[EntityId]):
    """
    A base class for all aggregate roots.
    Consists of 1+ entities. Spans transaction boundaries.
    """

    events: list = Field(default_factory=list)

    def register_event(self, event: DomainEvent):
        self.events.append(event)

    def collect_events(self):
        events = self.events
        self.events = []
        return events
