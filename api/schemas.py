"""Pydantic schemas for API request/response validation."""

from datetime import date

from pydantic import BaseModel


class OrderLineInput(BaseModel):
    """Input schema for order line allocation requests."""

    orderid: str
    sku: str
    qty: int


class BatchInput(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: date | None = None
