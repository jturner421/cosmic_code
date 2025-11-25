"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel


class OrderLineInput(BaseModel):
    """Input schema for order line allocation requests."""

    orderid: str
    sku: str
    qty: int
