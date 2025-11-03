import sqlalchemy as sa

from db.orm import OrderLineORM, to_domain
from db.session import Database
from model import OrderLine


def test_orderline_mapper_can_load_lines():
    with Database().get_session() as session:
        session.execute(
            sa.text(
                "INSERT INTO order_lines (orderid, sku, qty) "
                "VALUES (:orderid, :sku, :qty)",
            ),
            [
                {"orderid": "order1", "sku": "RED-CHAIR", "qty": 12},
                {"orderid": "order1", "sku": "RED-TABLE", "qty": 13},
                {"orderid": "order2", "sku": "BLUE-LIPSTICK", "qty": 14},
            ],
        )
        orm_results = session.query(OrderLineORM).all()
        result = [to_domain(orm) for orm in orm_results]
        expected = [
            OrderLine("order1", "RED-CHAIR", 12),
            OrderLine("order1", "RED-TABLE", 13),
            OrderLine("order2", "BLUE-LIPSTICK", 14),
        ]
    assert result == expected
