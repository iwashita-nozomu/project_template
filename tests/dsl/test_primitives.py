# @dependency-start
# responsibility Tests the public function-discretization DSL.
# upstream implementation ../../python/docomo_bt_management/dsl/__init__.py exposes the DSL API.
# upstream implementation ../../python/docomo_bt_management/dsl/primitives.py implements the DSL.
# downstream implementation ../../jupyter/test_primitive.ipynb mirrors representative DSL examples.
# @dependency-end
"""Tests for DSL primitives."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np
import numpy.typing as npt
import pytest
from docomo_bt_management.dsl import D, DiscretizationRequest, discretization
from scipy.optimize import root


def _quadratic_solution(points: jnp.ndarray) -> jnp.ndarray:
    return 1.0 + points**2


def _nonlinear_residual(x: object, t: object) -> object:
    exact = 1.0 + t**2  # type: ignore[operator]
    return D(x, "t", order=2) + x**2 - (2.0 + exact**2)  # type: ignore[operator]


def test_public_surface_exports_expected_symbols() -> None:
    """Public DSL import exposes only the intended primitives."""
    from docomo_bt_management import dsl

    assert set(dsl.__all__) == {"D", "DiscretizationRequest", "discretization"}


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
