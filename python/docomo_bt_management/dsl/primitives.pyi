# @dependency-start
# responsibility Describes public types for DSL primitives.
# upstream implementation ./primitives.py implements the runtime DSL.
# downstream implementation ./__init__.py re-exports the public DSL surface.
# @dependency-end
"""Type stubs for scalar function discretization primitives."""

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias, overload

from jaxtyping import Array, DTypeLike

DifferenceScheme: TypeAlias = Literal["forward", "backward", "central"]
PointwiseScalarFunction: TypeAlias = Callable[..., object]
DiscreteScalarFunction: TypeAlias = Callable[[Array], Array]
NamedInputBlocks: TypeAlias = dict[str, Array]


class _RestoredInputBlocks(Protocol):
    """Restored named variable blocks with output-aligned metadata."""

    @property
    def output_values(self) -> Mapping[str, Array]:
        """Return source values aligned with ``f_tilde`` output positions."""
        ...

    @property
    def f_tilde_shape(self) -> tuple[int, ...]:
        """Return the output shape produced by ``f_tilde``."""
        ...

    @property
    def z_shape(self) -> tuple[int, ...]:
        """Return the stacked input shape expected by ``f_tilde``."""
        ...

    def at_output(self, name: str) -> Array:
        """Return one source block aligned with ``f_tilde`` output positions."""
        ...

    def __getitem__(self, name: str) -> Array:
        """Return the full source block, including internal derivative samples."""
        ...

    def __iter__(self) -> Iterator[str]:
        """Iterate over source block names."""
        ...

    def __len__(self) -> int:
        """Return the number of source blocks."""
        ...


class BlockRestorer(Protocol):
    """Callable that restores named variable blocks from ``z``."""

    @property
    def f_tilde_shape(self) -> tuple[int, ...]:
        """Return the output shape produced by ``f_tilde``."""
        ...

    @property
    def z_shape(self) -> tuple[int, ...]:
        """Return the stacked input shape expected by ``f_tilde``."""
        ...

    @property
    def input_shape(self) -> tuple[int, ...]:
        """Return the internal shape for each source input block."""
        ...

    def names(self) -> tuple[str, ...]:
        """Return source block names in stack order."""
        ...

    def pack(self, **values_or_paths: object) -> Array:
        """Return ``z`` by sampling callables or stacking already sampled values."""
        ...

    def __call__(self, stacked_values: Array, /) -> _RestoredInputBlocks:
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


def finite_difference_matrix(
    grid: Array,
    scheme: DifferenceScheme,
    order: int,
    input_halo: int,
    *,
    dtype: DTypeLike = ...,
) -> Array: ...


def discretization(
    function: PointwiseScalarFunction,
    request: DiscretizationRequest,
) -> DiscretizationResult:
    """Return ``f_tilde(z)`` and a named-block restorer."""
    ...


__all__: list[str]
