import abc
from typing import Generic, TypeVar

from domain.entities import Entity as DomainEntity
from domain.value_objects import GenericUUID

Entity = TypeVar("Entity", bound=DomainEntity)
EntityId = TypeVar("EntityId", bound=GenericUUID)


class GenericRepository(Generic[Entity, EntityId], metaclass=abc.ABCMeta):
    """An interface for a generic repository"""

    @abc.abstractmethod
    def get(self, entity: Entity):
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, entity_id: EntityId) -> Entity:
        raise NotImplementedError

    def __getitem__(self, index) -> Entity:
        return self.get_by_id(index)
