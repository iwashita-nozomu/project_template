# @dependency-start
# responsibility Tests the public function-discretization DSL.
# upstream implementation ../../python/docomo_bt_management/dsl/__init__.py exposes the DSL API.
# upstream implementation ../../python/docomo_bt_management/dsl/primitives.py implements the DSL.
# downstream implementation ../../jupyter/test_primitive.ipynb mirrors representative DSL examples.
# @dependency-end
"""Tests for DSL primitives."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import jax.numpy as jnp
import numpy as np
import numpy.typing as npt
import pytest
from docomo_bt_management.dsl import D, DiscretizationRequest, discretization
from docomo_bt_management.dsl.primitives import finite_difference_matrix
from scipy.optimize import root


def _quadratic_solution(points: jnp.ndarray) -> jnp.ndarray:
    return 1.0 + points**2


def _square_path(points: jnp.ndarray) -> jnp.ndarray:
    return points**2


def _quartic_path(points: jnp.ndarray) -> jnp.ndarray:
    return points**4


def _shifted_quadratic_path(points: jnp.ndarray) -> jnp.ndarray:
    return 1.0 + points**2


def _linear_offset_path(points: jnp.ndarray) -> jnp.ndarray:
    return 2.0 + points


def _nonlinear_residual(x: object, t: object) -> object:
    exact = 1.0 + t**2  # type: ignore[operator]
    return D(x, "t", order=2) + x**2 - (2.0 + exact**2)  # type: ignore[operator]


def test_public_surface_exports_expected_symbols() -> None:
    """Public DSL import exposes only the intended primitives."""
    from docomo_bt_management import dsl

    assert set(dsl.__all__) == {"D", "DiscretizationRequest", "discretization"}


def test_callable_derivative_and_finite_difference_matrix() -> None:
    """Direct primitives keep their callable and matrix behavior."""

    def cubic_path(t: jnp.ndarray) -> jnp.ndarray:
        return t**3

    second_derivative = cast(Callable[[jnp.ndarray], jnp.ndarray], D(cubic_path, "t", order=2))
    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    forward_samples = jnp.linspace(0.0, 1.25, 6, dtype=jnp.float64)
    forward_matrix = finite_difference_matrix(
        grid,
        "forward",
        1,
        1,
        dtype=jnp.float64,
    )

    assert jnp.allclose(second_derivative(jnp.asarray(2.0)), 12.0)
    assert jnp.allclose(forward_matrix @ forward_samples, jnp.ones_like(grid))
    with pytest.raises(ValueError, match="Only derivatives"):
        D(cubic_path, "x")  # type: ignore[call-overload]
    with pytest.raises(ValueError, match="positive"):
        D(cubic_path, "t", order=0)
    with pytest.raises(TypeError, match="callable scalar path"):
        D(1.0, "t")


def test_high_order_central_difference_matches_polynomials() -> None:
    """Second and fourth derivatives match polynomial manufactured data."""

    def second_order_polynomial(x: object, t: object) -> object:
        return D(x, "t", order=2) + x  # type: ignore[operator]

    def fourth_order_polynomial(x: object, t: object) -> object:
        return D(x, "t", order=4) + x  # type: ignore[operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    second_tilde, second_blocks = discretization(
        second_order_polynomial,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    fourth_tilde, fourth_blocks = discretization(
        fourth_order_polynomial,
        DiscretizationRequest(grid=grid, scheme="central"),
    )

    second_samples = second_blocks.pack(x=_square_path)
    fourth_samples = fourth_blocks.pack(x=_quartic_path)

    assert jnp.allclose(second_tilde(second_samples), 2.0 + grid**2, atol=1e-4)
    assert jnp.allclose(fourth_tilde(fourth_samples), 24.0 + grid**4, atol=1e-3)


def test_discretizes_derivative_of_user_expression() -> None:
    """``D(jnp.sin(x), "t")`` samples the expression before differencing."""

    def residual(x: object, t: object) -> object:
        return D(jnp.sin(x), "t") + x  # type: ignore[arg-type, operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    f_tilde, restore_blocks = discretization(
        residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    x_samples = restore_blocks.pack(x=_shifted_quadratic_path)
    blocks = restore_blocks(x_samples)
    step = grid[1] - grid[0]
    expression_samples = jnp.sin(blocks["x"])
    expected_expression_derivative = (
        expression_samples[2:] - expression_samples[:-2]
    ) / (2.0 * step)

    assert blocks["x"].shape == restore_blocks.input_shape
    assert blocks.f_tilde_shape == restore_blocks.f_tilde_shape == (5,)
    assert jnp.allclose(
        f_tilde(x_samples),
        expected_expression_derivative + blocks.at_output("x"),
        atol=1e-6,
    )


def test_discretizes_user_function_of_derivative() -> None:
    """Normal user functions compose with the array returned by ``D``."""

    def residual(x: object, t: object) -> object:
        return jnp.sin(D(x, "t")) + x  # type: ignore[arg-type, operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    f_tilde, restore_blocks = discretization(
        residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    x_samples = restore_blocks.pack(x=_square_path)

    assert jnp.allclose(f_tilde(x_samples), jnp.sin(2.0 * grid) + grid**2, atol=1e-6)


def test_expression_derivative_uses_shared_multi_input_halo() -> None:
    """Expression derivatives keep every input available on the same halo."""

    def residual(x: object, y: object, t: object) -> object:
        return D(jnp.sin(x + y), "t") + y  # type: ignore[arg-type, operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    f_tilde, restore_blocks = discretization(
        residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    z = restore_blocks.pack(x=_square_path, y=_linear_offset_path)
    blocks = restore_blocks(z)
    step = grid[1] - grid[0]
    expression_samples = jnp.sin(blocks["x"] + blocks["y"])
    expected_expression_derivative = (
        expression_samples[2:] - expression_samples[:-2]
    ) / (2.0 * step)

    assert blocks["x"].shape == restore_blocks.input_shape
    assert blocks["y"].shape == restore_blocks.input_shape
    assert jnp.allclose(
        f_tilde(z),
        expected_expression_derivative + blocks.at_output("y"),
        atol=1e-6,
    )


def test_non_derivative_jax_function_and_constant_residual() -> None:
    """Functions without ``D`` run directly and do not allocate halo values."""

    def residual(x: object, t: object) -> object:
        return jnp.exp(x) + t  # type: ignore[arg-type, operator]

    def constant_residual(t: object) -> object:
        return 3.0

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    f_tilde, restore_blocks = discretization(residual, DiscretizationRequest(grid=grid))
    constant_tilde, constant_blocks = discretization(
        constant_residual,
        DiscretizationRequest(grid=grid),
    )
    z = restore_blocks.pack(x=_square_path)

    blocks = restore_blocks(z)
    assert blocks["x"].shape == restore_blocks.input_shape == (5,)
    assert blocks.at_output("x").shape == restore_blocks.f_tilde_shape
    assert jnp.allclose(f_tilde(z), jnp.exp(z) + grid)
    assert constant_blocks.names() == ()
    assert constant_blocks.f_tilde_shape == (5,)
    assert jnp.allclose(
        constant_tilde(constant_blocks.pack()),
        jnp.full((5,), 3.0, dtype=jnp.float64),
    )


def test_discretizes_nonlinear_manufactured_residual() -> None:
    """A nonlinear residual is zero on its manufactured solution."""
    grid = jnp.linspace(0.0, 1.0, 6, dtype=jnp.float64)
    f_tilde, restore_blocks = discretization(
        _nonlinear_residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    z = restore_blocks.pack(x=_quadratic_solution)

    residual = f_tilde(z)
    blocks = restore_blocks(z)

    assert restore_blocks.names() == ("x",)
    assert blocks["x"].shape == restore_blocks.input_shape
    assert residual.shape == blocks.f_tilde_shape == restore_blocks.f_tilde_shape
    assert jnp.allclose(residual, jnp.zeros_like(residual), atol=5e-5)


def test_solves_nonlinear_manufactured_system() -> None:
    """The nonlinear residual plus halo constraints recovers the solution."""
    grid = jnp.linspace(0.0, 1.0, 6, dtype=jnp.float64)
    f_tilde, restore_blocks = discretization(
        _nonlinear_residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    exact_z = restore_blocks.pack(x=_quadratic_solution)

    def residual(z_values: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        z_array = jnp.asarray(z_values, dtype=jnp.float64)
        ode_residual = np.asarray(f_tilde(z_array), dtype=float)
        boundary_residual = np.asarray(
            jnp.array([z_array[0] - exact_z[0], z_array[-1] - exact_z[-1]]),
            dtype=float,
        )
        return np.concatenate([ode_residual, boundary_residual])

    initial = np.asarray(exact_z + 0.05 * jnp.sin(jnp.arange(exact_z.size)), dtype=float)
    solution = root(residual, initial)

    assert solution.success
    assert np.linalg.norm(residual(solution.x), ord=np.inf) < 5e-5
    assert np.allclose(solution.x, np.asarray(exact_z), atol=2e-3)
    assert np.allclose(
        np.asarray(
            restore_blocks(jnp.asarray(solution.x, dtype=jnp.float64)).at_output("x")
        ),
        np.asarray(restore_blocks(exact_z).at_output("x")),
        atol=2e-3,
    )


def test_rejects_invalid_runtime_shape_and_signature() -> None:
    """Bad z length and non-final t signatures fail clearly."""

    def residual(x: object, t: object) -> object:
        return D(x, "t", order=2) + x  # type: ignore[operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    f_tilde, restore_blocks = discretization(residual, DiscretizationRequest(grid=grid))
    z = restore_blocks.pack(x=_square_path)

    with pytest.raises(TypeError):
        f_tilde(z[:-1])
    with pytest.raises(TypeError):
        f_tilde(jnp.concatenate([z, jnp.array([0.0], dtype=z.dtype)]))

    def missing_t(x: object) -> object:
        return x

    def misplaced_t(x: object, t: object, y: object) -> object:
        return x + y + t  # type: ignore[operator]

    with pytest.raises(ValueError, match="time argument t"):
        discretization(missing_t, DiscretizationRequest(grid=grid))
    with pytest.raises(ValueError, match="time argument t"):
        discretization(misplaced_t, DiscretizationRequest(grid=grid))


def test_restorer_rejects_bad_pack_inputs() -> None:
    """Restorer packing fails before callers can build malformed ``z`` blocks."""

    def residual(x: object, t: object) -> object:
        return D(x, "t") + x  # type: ignore[operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    _f_tilde, restore_blocks = discretization(residual, DiscretizationRequest(grid=grid))

    with pytest.raises(ValueError, match="expected inputs x; got <none>"):
        restore_blocks.pack()
    with pytest.raises(ValueError, match="expected inputs x; got x, y"):
        restore_blocks.pack(x=_square_path, y=_square_path)
    with pytest.raises(ValueError, match="must produce shape"):
        restore_blocks.pack(x=grid)
