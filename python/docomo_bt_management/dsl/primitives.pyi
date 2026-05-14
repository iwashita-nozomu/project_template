# @dependency-start
# responsibility Describes public types for DSL primitives.
# upstream implementation ./primitives.py implements the runtime DSL.
# downstream implementation ./__init__.py re-exports the public DSL surface.
# @dependency-end
"""Type stubs for scalar function discretization primitives."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias, overload

from jaxtyping import Array

DifferenceScheme: TypeAlias = Literal["forward", "backward", "central"]
PointwiseScalarFunction: TypeAlias = Callable[..., object]
DiscreteScalarFunction: TypeAlias = Callable[[Array], Array]
NamedInputBlocks: TypeAlias = dict[str, Array]


class BlockRestorer(Protocol):
    """Callable that restores named variable blocks from ``z``."""

    def names(self) -> tuple[str, ...]:
        """Return source block names in stack order."""
        ...

    def __call__(self, stacked_values: Array, /) -> NamedInputBlocks:
        """Return named source blocks from a vector shaped like ``z``."""
        ...


DiscretizationResult: TypeAlias = tuple[DiscreteScalarFunction, BlockRestorer]


@dataclass(frozen=True)
class DiscretizationRequest:
    """Request for discretizing ``f(x, y, ..., t)``."""

    grid: Array
    scheme: DifferenceScheme = "central"


@overload
def D(
    value: Callable[..., object],
    coordinate: Literal["t"],
    *,
    order: int = 1,
) -> Callable[..., object]: ...


@overload
def D(value: object, coordinate: Literal["t"], *, order: int = 1) -> object: ...


def discretization(
    function: PointwiseScalarFunction,
    request: DiscretizationRequest,
) -> DiscretizationResult:
    """Return ``f_tilde(z)`` and a named-block restorer."""
    ...


__all__: list[str]
