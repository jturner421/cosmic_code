# Allocation Tests Overview

This document explains what `tests/test_allocate.py` verifies about the domain model defined in `model.py`.

## Domain Concepts Under Test
- `OrderLine`: immutable request for a specific SKU and quantity.
- `Batch`: purchased inventory with a SKU, quantity, and optional `eta`; tracks allocations and ensures available quantity matches purchased stock minus allocations.
- `allocate_batch(line, batches)`: sorts candidate batches by arrival date, allocates the first batch that can satisfy the line, and raises `OutOfStock` when no batch can fulfill the request.

## Test Expectations
### `test_prefers_current_stock_batches_to_shipments`
- Creates an in-stock batch (`eta=None`) and a future shipment for the same SKU.
- Expects `allocate_batch` to consume from in-stock inventory first, leaving shipment stock untouched.

### `test_prefers_earlier_batches`
- Provides three dated batches for the same SKU.
- Confirms `allocate_batch` chooses the earliest arrival, leaving later batches fully available.

### `test_returns_allocated_batch_ref`
- Allocates against two eligible batches.
- Verifies that `allocate_batch` returns the reference of the batch that received the order line.

### `test_raises_out_of_stock_exception_if_cannot_allocate`
- Allocates an entire batch, exhausting its quantity.
- Attempts a second allocation for the same SKU and asserts an `OutOfStock` exception is raised, proving that over-allocation is blocked.
