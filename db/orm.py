from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.orm import registry

from model import OrderLine

mapper_registry = registry()

order_lines = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)


class OrderLineORM:
    """ORM model for OrderLine - mutable for SQLAlchemy"""
    pass


mapper_registry.map_imperatively(OrderLineORM, order_lines)


def to_domain(orm_line: OrderLineORM) -> OrderLine:
    """Convert ORM model to domain model"""
    return OrderLine(
        orderid=orm_line.orderid,
        sku=orm_line.sku,
        qty=orm_line.qty,
    )


def to_orm(domain_line: OrderLine) -> OrderLineORM:
    """Convert domain model to ORM model"""
    orm = OrderLineORM()
    orm.orderid = domain_line.orderid
    orm.sku = domain_line.sku
    orm.qty = domain_line.qty
    return orm
