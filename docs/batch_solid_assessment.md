# Batch Class Assessment

## Behaviour by Method
- `__init__(ref, sku, qty, eta)`: stores identifying data, total purchased quantity, and initialises `_allocations` as an empty `set[OrderLine]` to enforce uniqueness and enable efficient membership updates.
- `__repr__()`: returns `<Batch {reference}>` for concise debugging output without leaking full state.
- `__eq__(other)` and `__hash__()`: treat batches as identity objects keyed by `reference`, allowing instances to reside in sets and dictionaries while ensuring two batches with the same reference compare equal.
- `__gt__(other)`: encodes prioritisation rules used during allocation sorting—stock on hand (`eta=None`) beats shipments, and earlier shipment dates outrank later ones.
- `allocate(line)`: guards with `can_allocate` before adding the line to `_allocations`, making the method idempotent thanks to set semantics.
- `deallocate(line)`: safely removes a line if present, allowing rollbacks without raising exceptions when the line is absent.
- `allocated_quantity`: sums `qty` over `_allocations`, providing the committed units snapshot.
- `available_quantity`: returns `_purchased_quantity` minus `allocated_quantity`, keeping free stock derived from current allocations.
- `can_allocate(line)`: centralises the business rule—matching SKU and sufficient available quantity—for both internal and external checks.

## SOLID Evaluation
- **Single Responsibility Principle**: Mostly satisfied; the class tracks inventory state and exposes domain operations. The embedded ordering policy in `__gt__` hints at a secondary concern, which could be extracted if different ranking rules are expected.
- **Open/Closed Principle**: Moderately compliant; adding new allocation policies or eligibility rules requires editing existing methods (`can_allocate`, `__gt__`). Introducing strategy objects would improve openness.
- **Liskov Substitution Principle**: Upheld, provided subclasses respect the allocation contract (set-backed storage, quantity checks). Nothing in the implementation prevents substitutable behaviour.
- **Interface Segregation Principle**: Effectively satisfied. Clients consume a cohesive interface focused on allocation; there are no coarse-grained interfaces that force unnecessary dependencies.
- **Dependency Inversion Principle**: Satisfied in context. `Batch` relies only on the value object `OrderLine` and standard library types, keeping high-level policy (`allocate`) independent of infrastructure details. Further inversion could be pursued if external services enter the picture.

## Improvement Ideas
1. Extract the ordering policy from `__gt__` into a comparator or strategy to tighten SRP and aid extensibility.
2. Introduce pluggable allocation rules if variants such as backorders or reservations are anticipated, enhancing compliance with the Open/Closed Principle.
