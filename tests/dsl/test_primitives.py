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


def _nonlinear_residual(x: object, t: object) -> object:
    exact = 1.0 + t**2  # type: ignore[operator]
    return D(x, "t", order=2) + x**2 - (2.0 + exact**2)  # type: ignore[operator]


def _central_halo_points(grid: jnp.ndarray, halo: int) -> jnp.ndarray:
    left_halo = halo // 2
    offsets = jnp.arange(grid.size + halo, dtype=grid.dtype) - left_halo
    return grid[0] + offsets * (grid[1] - grid[0])


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
    second_tilde, _ = discretization(
        second_order_polynomial,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    fourth_tilde, _ = discretization(
        fourth_order_polynomial,
        DiscretizationRequest(grid=grid, scheme="central"),
    )

    second_halo_points = jnp.linspace(-0.25, 1.25, 7, dtype=jnp.float64)
    fourth_halo_points = jnp.linspace(-0.5, 1.5, 9, dtype=jnp.float64)

    assert jnp.allclose(second_tilde(second_halo_points**2), 2.0 + grid**2, atol=1e-4)
    assert jnp.allclose(fourth_tilde(fourth_halo_points**4), 24.0 + grid**4, atol=1e-3)


def test_discretizes_derivative_of_user_expression() -> None:
    """``D(jnp.sin(x), "t")`` samples the expression before differencing."""

    def residual(x: object, t: object) -> object:
        return D(jnp.sin(x), "t") + x  # type: ignore[arg-type, operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    halo_points = _central_halo_points(grid, 2)
    x_samples = 1.0 + halo_points**2
    f_tilde, restore_blocks = discretization(
        residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    step = grid[1] - grid[0]
    expected_expression_derivative = (
        jnp.sin(x_samples[2:]) - jnp.sin(x_samples[:-2])
    ) / (2.0 * step)

    assert restore_blocks(x_samples)["x"].shape == (7,)
    assert jnp.allclose(
        f_tilde(x_samples),
        expected_expression_derivative + (1.0 + grid**2),
        atol=1e-6,
    )


def test_discretizes_user_function_of_derivative() -> None:
    """Normal user functions compose with the array returned by ``D``."""

    def residual(x: object, t: object) -> object:
        return jnp.sin(D(x, "t")) + x  # type: ignore[arg-type, operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    halo_points = _central_halo_points(grid, 2)
    x_samples = halo_points**2
    f_tilde, _ = discretization(
        residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )

    assert jnp.allclose(f_tilde(x_samples), jnp.sin(2.0 * grid) + grid**2, atol=1e-6)


def test_expression_derivative_uses_shared_multi_input_halo() -> None:
    """Expression derivatives keep every input available on the same halo."""

    def residual(x: object, y: object, t: object) -> object:
        return D(jnp.sin(x + y), "t") + y  # type: ignore[arg-type, operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    halo_points = _central_halo_points(grid, 2)
    x_samples = halo_points**2
    y_samples = 2.0 + halo_points
    z = jnp.concatenate([x_samples, y_samples])
    f_tilde, restore_blocks = discretization(
        residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    blocks = restore_blocks(z)
    step = grid[1] - grid[0]
    expression_samples = jnp.sin(x_samples + y_samples)
    expected_expression_derivative = (
        expression_samples[2:] - expression_samples[:-2]
    ) / (2.0 * step)

    assert blocks["x"].shape == (7,)
    assert blocks["y"].shape == (7,)
    assert jnp.allclose(
        f_tilde(z),
        expected_expression_derivative + (2.0 + grid),
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
    z = grid**2

    assert restore_blocks(z)["x"].shape == (5,)
    assert jnp.allclose(f_tilde(z), jnp.exp(z) + grid)
    assert constant_blocks.names() == ()
    assert jnp.allclose(
        constant_tilde(jnp.array([], dtype=jnp.float64)),
        jnp.full((5,), 3.0, dtype=jnp.float64),
    )


def test_discretizes_nonlinear_manufactured_residual() -> None:
    """A nonlinear residual is zero on its manufactured solution."""
    grid = jnp.linspace(0.0, 1.0, 6, dtype=jnp.float64)
    f_tilde, restore_blocks = discretization(
        _nonlinear_residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )
    halo_points = jnp.linspace(-0.2, 1.2, 8, dtype=jnp.float64)
    z = _quadratic_solution(halo_points)

    residual = f_tilde(z)
    blocks = restore_blocks(z)

    assert restore_blocks.names() == ("x",)
    assert blocks["x"].shape == (8,)
    assert residual.shape == (6,)
    assert jnp.allclose(residual, jnp.zeros_like(residual), atol=5e-5)


def test_solves_nonlinear_manufactured_system() -> None:
    """The nonlinear residual plus halo constraints recovers the solution."""
    grid = jnp.linspace(0.0, 1.0, 6, dtype=jnp.float64)
    halo_points = jnp.linspace(-0.2, 1.2, 8, dtype=jnp.float64)
    exact_z = _quadratic_solution(halo_points)
    f_tilde, restore_blocks = discretization(
        _nonlinear_residual,
        DiscretizationRequest(grid=grid, scheme="central"),
    )

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
        np.asarray(restore_blocks(jnp.asarray(solution.x, dtype=jnp.float64))["x"][1:-1]),
        np.asarray(_quadratic_solution(grid)),
        atol=2e-3,
    )


def test_rejects_invalid_runtime_shape_and_signature() -> None:
    """Bad z length and non-final t signatures fail clearly."""

    def residual(x: object, t: object) -> object:
        return D(x, "t", order=2) + x  # type: ignore[operator]

    grid = jnp.linspace(0.0, 1.0, 5, dtype=jnp.float64)
    f_tilde, _ = discretization(residual, DiscretizationRequest(grid=grid))
    z = jnp.linspace(-0.25, 1.25, 7, dtype=jnp.float64)

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
