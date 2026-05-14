# @dependency-start
# responsibility Defines scalar-path discretization primitives.
# upstream design ../../../documents/functional-discretization-design.md DSL direction.
# upstream implementation ../../../docker/requirements.txt declares JAX and jax_util dependencies.
# downstream implementation ./__init__.py exports discretization.
# @dependency-end
"""Scalar function discretization primitives."""

from __future__ import annotations

import inspect
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import FunctionType
from typing import Literal, TypeAlias

import jax
import jax.numpy as jnp
from jaxtyping import Array, DTypeLike

DifferenceScheme: TypeAlias = Literal["forward", "backward", "central"]
PointwiseScalarFunction: TypeAlias = Callable[..., object]
DiscreteScalarFunction: TypeAlias = Callable[[Array], Array]
NamedInputBlocks: TypeAlias = dict[str, Array]
BlockRestorer: TypeAlias = Callable[[Array], NamedInputBlocks]
DiscretizationResult: TypeAlias = tuple[DiscreteScalarFunction, BlockRestorer]
UNSUPPORTED_PARAMETER_KINDS = (
    inspect.Parameter.KEYWORD_ONLY,
    inspect.Parameter.VAR_KEYWORD,
    inspect.Parameter.VAR_POSITIONAL,
)


@dataclass(frozen=True)
class DerivativeMarker:
    """Marker for a derivative argument in a pointwise function signature."""

    source_name: str
    order: int = 1


@dataclass(frozen=True)
class SymbolicExpression:
    """Expression traced from a pointwise function before discretization."""

    code: str
    source_name: str | None = None
    input_names: frozenset[str] = frozenset()
    derivatives: frozenset[DerivativeMarker] = frozenset()

    @classmethod
    def variable(cls, name: str) -> SymbolicExpression:
        """Return a symbolic function argument."""
        if name == "t":
            return cls("grid_points")
        return cls(f"value_{name}", name, frozenset({name}))

    @classmethod
    def constant(cls, value: object) -> SymbolicExpression:
        """Return a scalar constant expression."""
        if isinstance(value, int | float):
            return cls(repr(value))
        raise TypeError("Pointwise function must return a symbolic scalar expression.")

    def coerce(self, other: object) -> SymbolicExpression:
        if isinstance(other, SymbolicExpression):
            return other
        return self.constant(other)

    def __add__(self, other: object) -> SymbolicExpression:  # noqa: D105
        rhs = self.coerce(other)
        return SymbolicExpression(
            f"({self.code} + {rhs.code})",
            input_names=self.input_names | rhs.input_names,
            derivatives=self.derivatives | rhs.derivatives,
        )

    def __radd__(self, other: object) -> SymbolicExpression:  # noqa: D105
        lhs = self.coerce(other)
        return SymbolicExpression(
            f"({lhs.code} + {self.code})",
            input_names=lhs.input_names | self.input_names,
            derivatives=lhs.derivatives | self.derivatives,
        )

    def __sub__(self, other: object) -> SymbolicExpression:  # noqa: D105
        rhs = self.coerce(other)
        return SymbolicExpression(
            f"({self.code} - {rhs.code})",
            input_names=self.input_names | rhs.input_names,
            derivatives=self.derivatives | rhs.derivatives,
        )

    def __rsub__(self, other: object) -> SymbolicExpression:  # noqa: D105
        lhs = self.coerce(other)
        return SymbolicExpression(
            f"({lhs.code} - {self.code})",
            input_names=lhs.input_names | self.input_names,
            derivatives=lhs.derivatives | self.derivatives,
        )

    def __mul__(self, other: object) -> SymbolicExpression:  # noqa: D105
        rhs = self.coerce(other)
        return SymbolicExpression(
            f"({self.code} * {rhs.code})",
            input_names=self.input_names | rhs.input_names,
            derivatives=self.derivatives | rhs.derivatives,
        )

    def __rmul__(self, other: object) -> SymbolicExpression:  # noqa: D105
        lhs = self.coerce(other)
        return SymbolicExpression(
            f"({lhs.code} * {self.code})",
            input_names=lhs.input_names | self.input_names,
            derivatives=lhs.derivatives | self.derivatives,
        )

    def __truediv__(self, other: object) -> SymbolicExpression:  # noqa: D105
        rhs = self.coerce(other)
        return SymbolicExpression(
            f"({self.code} / {rhs.code})",
            input_names=self.input_names | rhs.input_names,
            derivatives=self.derivatives | rhs.derivatives,
        )

    def __rtruediv__(self, other: object) -> SymbolicExpression:  # noqa: D105
        lhs = self.coerce(other)
        return SymbolicExpression(
            f"({lhs.code} / {self.code})",
            input_names=lhs.input_names | self.input_names,
            derivatives=lhs.derivatives | self.derivatives,
        )

    def __pow__(self, other: object) -> SymbolicExpression:  # noqa: D105
        rhs = self.coerce(other)
        return SymbolicExpression(
            f"({self.code} ** {rhs.code})",
            input_names=self.input_names | rhs.input_names,
            derivatives=self.derivatives | rhs.derivatives,
        )

    def __rpow__(self, other: object) -> SymbolicExpression:  # noqa: D105
        lhs = self.coerce(other)
        return SymbolicExpression(
            f"({lhs.code} ** {self.code})",
            input_names=lhs.input_names | self.input_names,
            derivatives=lhs.derivatives | self.derivatives,
        )

    def __neg__(self) -> SymbolicExpression:  # noqa: D105
        return SymbolicExpression(
            f"(-{self.code})",
            input_names=self.input_names,
            derivatives=self.derivatives,
        )


def D(value: object, coordinate: str, *, order: int = 1) -> object:
    """Mark a time derivative expression."""
    if coordinate != "t":
        raise ValueError("Only derivatives with respect to t are supported.")
    if order < 1:
        raise ValueError("Derivative order must be positive.")
    if isinstance(value, SymbolicExpression):
        if value.source_name is None:
            raise TypeError("D expects a direct scalar path argument.")
        marker = DerivativeMarker(value.source_name, order)
        return SymbolicExpression(
            f"derivative_{value.source_name}_{order}",
            derivatives=frozenset({marker}),
        )
    if callable(value):
        derivative = value
        for _ in range(order):
            derivative = jax.grad(derivative)
        return derivative
    raise TypeError("D expects a symbolic path or callable scalar path.")


@dataclass(frozen=True)
class DiscretizationRequest:
    """Request for discretizing a pointwise scalar function."""

    grid: Array
    scheme: DifferenceScheme = "central"


@dataclass(frozen=True)
class InputBlockRestorer:
    """Callable layout for restoring named input blocks from ``z``."""

    input_slices: Mapping[str, slice]
    total_width: int

    def names(self) -> tuple[str, ...]:
        """Return source block names in stack order."""
        return tuple(self.input_slices)

    def __call__(self, stacked_values: Array, /) -> NamedInputBlocks:
        """Return named source blocks from a vector shaped like ``z``."""
        stacked_values = jnp.reshape(stacked_values, (self.total_width,))
        return {
            name: stacked_values[input_slice]
            for name, input_slice in self.input_slices.items()
        }


def finite_difference_matrix(
    grid: Array,
    scheme: DifferenceScheme,
    order: int,
    input_halo: int,
    *,
    dtype: DTypeLike = jnp.float64,
) -> Array:
    """Build a finite-difference matrix for the requested derivative order."""
    if order < 0:
        raise ValueError("Derivative order must be non-negative.")
    if input_halo < 0:
        raise ValueError("input_halo must be non-negative.")
    grid = jnp.asarray(grid)
    output_count = len(grid)
    if scheme == "forward":
        offsets = tuple(range(order + 1))
        left_halo = 0
        required_halo = order
    elif scheme == "backward":
        offsets = tuple(range(-order, 1))
        left_halo = input_halo
        required_halo = order
    elif scheme == "central":
        radius = math.ceil(order / 2)
        offsets = tuple(range(-radius, radius + 1))
        left_halo = input_halo // 2
        required_halo = 2 * radius
    else:
        raise ValueError(f"Unknown difference scheme: {scheme}")
    if input_halo < required_halo:
        raise ValueError("input_halo is too small for the requested derivative.")
    columns = output_count + input_halo
    matrix = jnp.zeros((output_count, columns), dtype=dtype)
    rows = jnp.arange(output_count)
    stencil_points = jnp.asarray(offsets, dtype=dtype)
    vandermonde = jnp.stack(
        [stencil_points**power for power in range(len(offsets))]
    )
    target = jnp.zeros((len(offsets),), dtype=dtype).at[order].set(
        math.factorial(order)
    )
    weights = jnp.linalg.solve(vandermonde, target) / ((grid[1] - grid[0]) ** order)
    base_columns = rows + left_halo + offsets[0]
    for index, weight in enumerate(weights):
        matrix = matrix.at[rows, base_columns + index].set(weight)
    return matrix


def discretization(
    function: PointwiseScalarFunction,
    request: DiscretizationRequest,
) -> DiscretizationResult:
    """Return ``f_tilde(z)`` and a restorer for the named input blocks in ``z``."""
    grid = jnp.asarray(request.grid)
    parameters = tuple(inspect.signature(function).parameters.values())
    if any(parameter.kind in UNSUPPORTED_PARAMETER_KINDS for parameter in parameters):
        raise TypeError("discretization requires positional pointwise arguments.")
    parameter_names = tuple(parameter.name for parameter in parameters)
    if not parameter_names or parameter_names[-1] != "t":
        raise ValueError("Pointwise function must end with the time argument t.")
    input_names = parameter_names[:-1]
    symbolic_args = tuple(SymbolicExpression.variable(name) for name in parameter_names)
    expression = function(*symbolic_args)
    if not isinstance(expression, SymbolicExpression):
        expression = SymbolicExpression.constant(expression)
    source_halos = dict.fromkeys(input_names, 0)
    input_order = {name: index for index, name in enumerate(input_names)}
    derivatives = tuple(
        sorted(expression.derivatives, key=lambda item: (input_order[item.source_name], item.order))
    )
    for derivative in derivatives:
        if derivative.source_name not in source_halos:
            raise ValueError(f"Missing derivative source: {derivative.source_name}")
        halo = (
            2 * math.ceil(derivative.order / 2)
            if request.scheme == "central"
            else derivative.order
        )
        source_halos[derivative.source_name] = max(source_halos[derivative.source_name], halo)
    output_count = len(grid)
    input_widths = {name: output_count + source_halos[name] for name in input_names}
    input_slices: dict[str, slice] = {}
    total_width = 0
    for name, width in input_widths.items():
        input_slices[name] = slice(total_width, total_width + width)
        total_width += width

    block_restorer = InputBlockRestorer(input_slices, total_width)
    namespace: dict[str, object] = {
        "grid_points": grid,
        "reshape": jnp.reshape,
        "total_shape": (total_width,),
    }
    generated_lines = [
        "def f_tilde(stacked_values):",
        "    stacked_values = reshape(stacked_values, total_shape)",
    ]
    for index, name in enumerate(input_names):
        namespace[f"input_slice_{index}"] = input_slices[name]
        namespace[f"matrix_{index}"] = finite_difference_matrix(
            grid, request.scheme, 0, source_halos[name],
            dtype=grid.dtype,
        )
        generated_lines.append(
            f"    value_{name} = matrix_{index} @ stacked_values[input_slice_{index}]"
        )
    for index, derivative in enumerate(derivatives):
        namespace[f"derivative_slice_{index}"] = input_slices[derivative.source_name]
        namespace[f"derivative_matrix_{index}"] = finite_difference_matrix(
            grid, request.scheme, derivative.order, source_halos[derivative.source_name],
            dtype=grid.dtype,
        )
        generated_lines.append(
            f"    derivative_{derivative.source_name}_{derivative.order} = "
            f"derivative_matrix_{index} @ stacked_values[derivative_slice_{index}]"
        )
    generated_lines.append(f"    return {expression.code}")
    exec("\n".join(generated_lines), namespace)  # noqa: S102
    generated_f_tilde = namespace["f_tilde"]
    if not isinstance(generated_f_tilde, FunctionType):
        raise TypeError("Generated discretized function is not callable.")

    def f_tilde(stacked_values: Array) -> Array:
        return generated_f_tilde(stacked_values)

    return f_tilde, block_restorer


__all__ = [
    "D",
    "DiscretizationRequest",
    "discretization",
]
