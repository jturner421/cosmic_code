from repository import AbstractRepository, Entity, EntityId


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, entity: Entity):
        self.session.add(entity)

    def get_by_id(self, entity_id: EntityId) -> Entity:
        return self.session.query(Entity).filter_by(entity_id).one_or_none()

    def list(self):
        return self.session.query(Entity).all()
