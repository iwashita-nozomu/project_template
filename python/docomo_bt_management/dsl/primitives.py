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
from collections.abc import Callable, Iterator, Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Literal, TypeAlias, cast

import jax
import jax.numpy as jnp
from jaxtyping import Array, DTypeLike

DifferenceScheme: TypeAlias = Literal["forward", "backward", "central"]
PointwiseScalarFunction: TypeAlias = Callable[..., object]
DiscreteScalarFunction: TypeAlias = Callable[[Array], Array]
NamedInputBlocks: TypeAlias = dict[str, Array]
InputPathOrSamples: TypeAlias = Callable[[Array], object] | object
BlockRestorer: TypeAlias = Callable[[Array], "_RestoredInputBlocks"]
DiscretizationResult: TypeAlias = tuple[DiscreteScalarFunction, BlockRestorer]
UNSUPPORTED_PARAMETER_KINDS = (
    inspect.Parameter.KEYWORD_ONLY,
    inspect.Parameter.VAR_KEYWORD,
    inspect.Parameter.VAR_POSITIONAL,
)


def _required_halo_width(scheme: DifferenceScheme, order: int) -> int:
    """Return the source halo width required by a finite-difference stencil."""
    if order < 0:
        raise ValueError("Derivative order must be non-negative.")
    if scheme == "forward" or scheme == "backward":
        return order
    if scheme == "central":
        return 2 * math.ceil(order / 2)
    raise ValueError(f"Unknown difference scheme: {scheme}")


def _left_halo_width(scheme: DifferenceScheme, input_halo: int) -> int:
    """Return how many halo samples appear before the grid-aligned samples."""
    if input_halo < 0:
        raise ValueError("input_halo must be non-negative.")
    if scheme == "forward":
        return 0
    if scheme == "backward":
        return input_halo
    if scheme == "central":
        return input_halo // 2
    raise ValueError(f"Unknown difference scheme: {scheme}")


@dataclass
class _DerivativeEvaluationContext:
    """Runtime state used by ``D`` while a function is being discretized."""

    grid: Array
    scheme: DifferenceScheme
    input_halo: int
    mode: Literal["probe", "runtime"]
    derivative_matrices: Mapping[int, Array]
    observed_orders: list[int]
    output_count: int
    input_width: int
    grid_slice: slice

    def apply_derivative(self, value: object, order: int) -> Array:
        """Apply or record a finite-difference derivative marker."""
        self.observed_orders.append(order)
        value_array = jnp.asarray(value)
        if self.mode == "probe":
            return jnp.zeros_like(value_array)
        return self._apply_runtime_derivative(value_array, order)

    def _apply_runtime_derivative(self, value: Array, order: int) -> Array:
        flattened = jnp.reshape(value, (-1,))
        if flattened.shape[0] != self.input_width:
            raise TypeError(
                "D inside discretization expects an expression sampled on "
                "the derivative halo."
            )
        matrix = self.derivative_matrices.get(order)
        if matrix is None:
            matrix = finite_difference_matrix(
                self.grid,
                self.scheme,
                order,
                self.input_halo,
                dtype=value.dtype,
            )
        derivative_values = matrix @ flattened
        embedded = jnp.zeros((self.input_width,), dtype=derivative_values.dtype)
        return embedded.at[self.grid_slice].set(derivative_values)


_ACTIVE_DERIVATIVE_CONTEXT: ContextVar[_DerivativeEvaluationContext | None] = (
    ContextVar("_ACTIVE_DERIVATIVE_CONTEXT", default=None)
)


def D(value: object, coordinate: str, *, order: int = 1) -> object:
    """Mark a time derivative expression."""
    if coordinate != "t":
        raise ValueError("Only derivatives with respect to t are supported.")
    if order < 1:
        raise ValueError("Derivative order must be positive.")
    context = _ACTIVE_DERIVATIVE_CONTEXT.get()
    if context is not None and not callable(value):
        return context.apply_derivative(value, order)
    if callable(value):
        derivative = value
        for _ in range(order):
            derivative = jax.grad(derivative)
        return derivative
    raise TypeError(
        "D expects a callable scalar path outside discretization or an array "
        "expression inside discretization."
    )


@dataclass(frozen=True)
class DiscretizationRequest:
    """Request for discretizing a pointwise scalar function."""

    interval: tuple[float, float]
    points: int
    scheme: DifferenceScheme = "central"

    def time_grid(self) -> Array:
        """Return the uniform grid implied by the interval and point count."""
        if self.points < 2:
            raise ValueError("points must be at least 2.")
        start, stop = self.interval
        return jnp.linspace(start, stop, self.points, dtype=jnp.float64)


@dataclass(frozen=True)
class _RestoredInputBlocks(Mapping[str, Array]):
    """Named input blocks restored from ``z`` with output-aligned metadata."""

    all_values: Mapping[str, Array]
    output_values: Mapping[str, Array]
    f_tilde_shape: tuple[int, ...]
    z_shape: tuple[int, ...]
    grid: Array

    def __getitem__(self, name: str) -> Array:
        """Return the full source block, including internal derivative samples."""
        return self.all_values[name]

    def __iter__(self) -> Iterator[str]:
        """Iterate over restored block names."""
        return iter(self.all_values)

    def __len__(self) -> int:
        """Return the number of restored source blocks."""
        return len(self.all_values)

    def at_output(self, name: str) -> Array:
        """Return values aligned with ``f_tilde`` output positions."""
        return self.output_values[name]


@dataclass(frozen=True)
class InputBlockRestorer:
    """Callable layout for restoring named input blocks from ``z``."""

    input_slices: Mapping[str, slice]
    total_width: int
    input_width: int
    f_tilde_shape: tuple[int, ...]
    grid: Array
    _output_slice: slice
    _sample_points: Array

    @property
    def z_shape(self) -> tuple[int, ...]:
        """Return the expected shape of the stacked ``z`` vector."""
        return (self.total_width,)

    @property
    def input_shape(self) -> tuple[int, ...]:
        """Return the internal per-input block shape."""
        return (self.input_width,)

    def names(self) -> tuple[str, ...]:
        """Return source block names in stack order."""
        return tuple(self.input_slices)

    def __call__(self, stacked_values: Array, /) -> _RestoredInputBlocks:
        """Return named source blocks from a vector shaped like ``z``."""
        return _restore_input_blocks(self, stacked_values)

    def pack(self, **values_or_paths: InputPathOrSamples) -> Array:
        """Return ``z`` by sampling paths on internal points or stacking samples."""
        return _pack_input_blocks(self, values_or_paths)


def _restore_input_blocks(
    restorer: InputBlockRestorer,
    stacked_values: Array,
) -> _RestoredInputBlocks:
    """Return restored input blocks with output-aligned values."""
    stacked_values = jnp.reshape(stacked_values, restorer.z_shape)
    output_slice = cast(slice, getattr(restorer, "_output_slice"))
    all_values = {
        name: stacked_values[input_slice]
        for name, input_slice in restorer.input_slices.items()
    }
    output_values = {
        name: values[output_slice]
        for name, values in all_values.items()
    }
    return _RestoredInputBlocks(
        all_values=all_values,
        output_values=output_values,
        f_tilde_shape=restorer.f_tilde_shape,
        z_shape=restorer.z_shape,
        grid=restorer.grid,
    )


def _pack_input_blocks(
    restorer: InputBlockRestorer,
    values_or_paths: Mapping[str, InputPathOrSamples],
) -> Array:
    """Return ``z`` by sampling paths on internal points or stacking samples."""
    expected_names = set(restorer.input_slices)
    provided_names = set(values_or_paths)
    if provided_names != expected_names:
        expected = ", ".join(restorer.input_slices) or "<none>"
        provided = ", ".join(sorted(provided_names)) or "<none>"
        raise ValueError(f"pack expected inputs {expected}; got {provided}.")
    blocks = [
        _coerce_input_block(restorer, name, values_or_paths[name])
        for name in restorer.input_slices
    ]
    if not blocks:
        sample_points = cast(Array, getattr(restorer, "_sample_points"))
        return jnp.zeros(restorer.z_shape, dtype=sample_points.dtype)
    return jnp.concatenate(blocks)


def _coerce_input_block(
    restorer: InputBlockRestorer,
    name: str,
    value_or_path: InputPathOrSamples,
) -> Array:
    """Return one input block shaped for the internal discretization layout."""
    sample_points = cast(Array, getattr(restorer, "_sample_points"))
    raw_values = value_or_path(sample_points) if callable(value_or_path) else value_or_path
    values = jnp.reshape(jnp.asarray(raw_values), (-1,))
    if values.shape[0] != restorer.input_width:
        raise ValueError(
            f"Input {name!r} must produce shape {restorer.input_shape}; "
            f"got {(values.shape[0],)}."
        )
    return values


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
    elif scheme == "backward":
        offsets = tuple(range(-order, 1))
    elif scheme == "central":
        radius = math.ceil(order / 2)
        offsets = tuple(range(-radius, radius + 1))
    else:
        raise ValueError(f"Unknown difference scheme: {scheme}")
    left_halo = _left_halo_width(scheme, input_halo)
    required_halo = _required_halo_width(scheme, order)
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


def _discretization_parameter_names(function: PointwiseScalarFunction) -> tuple[str, ...]:
    parameters = tuple(inspect.signature(function).parameters.values())
    if any(parameter.kind in UNSUPPORTED_PARAMETER_KINDS for parameter in parameters):
        raise TypeError("discretization requires positional pointwise arguments.")
    parameter_names = tuple(parameter.name for parameter in parameters)
    if not parameter_names or parameter_names[-1] != "t":
        raise ValueError("Pointwise function must end with the time argument t.")
    return parameter_names


def _probe_derivative_orders(
    function: PointwiseScalarFunction,
    input_names: tuple[str, ...],
    grid: Array,
    scheme: DifferenceScheme,
) -> tuple[int, ...]:
    output_count = int(grid.shape[0])
    probe_context = _DerivativeEvaluationContext(
        grid=grid,
        scheme=scheme,
        input_halo=0,
        mode="probe",
        derivative_matrices={},
        observed_orders=[],
        output_count=output_count,
        input_width=output_count,
        grid_slice=slice(0, output_count),
    )
    token = _ACTIVE_DERIVATIVE_CONTEXT.set(probe_context)
    try:
        function(*(jnp.zeros_like(grid) for _ in input_names), grid)
    finally:
        _ACTIVE_DERIVATIVE_CONTEXT.reset(token)
    return tuple(sorted(set(probe_context.observed_orders)))


def _normalize_discretized_result(
    result: object,
    output_count: int,
    input_width: int,
    grid_slice: slice,
) -> Array:
    result_array = jnp.asarray(result)
    if result_array.ndim == 0:
        return jnp.full((output_count,), result_array, dtype=result_array.dtype)
    flattened = jnp.reshape(result_array, (-1,))
    if flattened.shape[0] == input_width:
        return flattened[grid_slice]
    if flattened.shape[0] == output_count:
        return flattened
    raise TypeError(
        "Pointwise function must return a scalar, grid-sized expression, "
        "or halo-sized expression."
    )


def discretization(
    function: PointwiseScalarFunction,
    request: DiscretizationRequest,
) -> DiscretizationResult:
    """Return ``f_tilde(z)`` and a restorer for the named input blocks in ``z``."""
    grid = request.time_grid()
    if grid.ndim != 1 or grid.shape[0] < 2:
        raise ValueError("grid must be a one-dimensional array with at least two points.")
    parameter_names = _discretization_parameter_names(function)
    input_names = parameter_names[:-1]
    output_count = int(grid.shape[0])
    derivative_orders = _probe_derivative_orders(
        function,
        input_names,
        grid,
        request.scheme,
    )
    input_halo = max(
        (_required_halo_width(request.scheme, order) for order in derivative_orders),
        default=0,
    )
    left_halo = _left_halo_width(request.scheme, input_halo)
    input_width = output_count + input_halo
    grid_slice = slice(left_halo, left_halo + output_count)
    input_slices: dict[str, slice] = {}
    total_width = 0
    for name in input_names:
        input_slices[name] = slice(total_width, total_width + input_width)
        total_width += input_width

    time_offsets = jnp.arange(input_width, dtype=grid.dtype) - left_halo
    time_samples = grid[0] + time_offsets * (grid[1] - grid[0])
    block_restorer = InputBlockRestorer(
        input_slices=input_slices,
        total_width=total_width,
        input_width=input_width,
        f_tilde_shape=(output_count,),
        grid=grid,
        _output_slice=grid_slice,
        _sample_points=time_samples,
    )
    derivative_matrices = {
        order: finite_difference_matrix(
            grid,
            request.scheme,
            order,
            input_halo,
            dtype=grid.dtype,
        )
        for order in derivative_orders
    }
    def f_tilde(stacked_values: Array) -> Array:
        stacked_values = jnp.reshape(stacked_values, (total_width,))
        source_blocks = tuple(stacked_values[input_slices[name]] for name in input_names)
        context = _DerivativeEvaluationContext(
            grid=grid,
            scheme=request.scheme,
            input_halo=input_halo,
            mode="runtime",
            derivative_matrices=derivative_matrices,
            observed_orders=[],
            output_count=output_count,
            input_width=input_width,
            grid_slice=grid_slice,
        )
        token = _ACTIVE_DERIVATIVE_CONTEXT.set(context)
        try:
            result = function(*source_blocks, time_samples)
        finally:
            _ACTIVE_DERIVATIVE_CONTEXT.reset(token)
        return _normalize_discretized_result(
            result,
            output_count,
            input_width,
            grid_slice,
        )

    return f_tilde, block_restorer


__all__ = [
    "D",
    "DiscretizationRequest",
    "discretization",
]
