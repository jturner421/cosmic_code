"""
Repository pattern abstractions and implementations.

The repository pattern provides a collection-like interface for accessing domain objects,
abstracting away persistence details.
"""

import abc
from typing import Generic, TypeVar

from domain.entities import Entity as DomainEntity
from domain.value_objects import GenericUUID

Entity = TypeVar("Entity", bound=DomainEntity)
EntityId = TypeVar("EntityId", bound=GenericUUID)


class AbstractRepository(Generic[Entity, EntityId], metaclass=abc.ABCMeta):
    """
    An interface for a generic repository.

    Note: This abstract class is designed for UUID-based entities that inherit
    from domain.entities.Entity. For simpler domain models like Batch/OrderLine,
    see SqlAlchemyRepository, BatchRepository, and OrderLineRepository in
    repository.repositories.
    """

    @abc.abstractmethod
    def add(self, entity: Entity): ...

    @abc.abstractmethod
    def get_by_id(self, entity_id: EntityId) -> Entity: ...

    @abc.abstractmethod
    def list(self) -> list[Entity]: ...

    def __getitem__(self, index) -> Entity:
        return self.get_by_id(index)
