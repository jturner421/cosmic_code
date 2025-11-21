from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import registry, relationship

from model import Batch, OrderLine

mapper_registry = registry()
_mappings_configured = False
_mapping_state = {"configured": False}

order_lines = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

batches = Table(
    "batches",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_qty", Integer),
    Column("eta", Date),
)

allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def perform_mapping():
    """
    Map domain models to database tables using SQLAlchemy imperative mapping.

    This keeps domain models persistence-ignorant while allowing SQLAlchemy
    to handle database operations.
    """
    if _mapping_state["configured"]:
        return

    mapper_registry.map_imperatively(OrderLine, order_lines)
    mapper_registry.map_imperatively(
        Batch,
        batches,
        properties={
            "_purchased_quantity": batches.c._purchased_qty,  # noqa: SLF001
            "_allocations": relationship(
                OrderLine,
                secondary=allocations,
                collection_class=set,
            ),
        },
    )
    _mappings_configured = True
