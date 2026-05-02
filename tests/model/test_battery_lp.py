"""Tests for battery LP block assembly and LP problem wiring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import jax.numpy as jnp
import numpy as np
import pytest
from docomo_bt_management.model.battery_lp_builder import BatteryLPBuilder
from docomo_bt_management.model.LPproblem import optimal_control_lp
from jax_util.base import Vector

if TYPE_CHECKING:
    def _to_vector(value: object) -> Vector: ...
else:
    def _to_vector(value: object) -> Vector:
        return jnp.asarray(value, dtype=jnp.float32)


def _vector(values: list[float]) -> Vector:
    """Build a typed JAX vector for tests."""
    return _to_vector(values)


def _allclose(left: object, right: object) -> bool:
    """Return a Python bool from `jnp.allclose`."""
    return bool(np.allclose(np.asarray(left), np.asarray(right)))


def test_battery_lp_builder_assemble_keeps_block_shapes_consistent() -> None:
    """The builder should emit consistent block row counts and horizon widths."""
    horizon = 3
    model = BatteryLPBuilder(
        horizon=horizon,
        efficiency=0.9,
        pcs_capacity=2.0,
        charge_rate=1.5,
        B_lower=0.0,
        B_upper=4.0,
        loss=0.01,
    ).assemble()

    assert model.dtype == jnp.float32
    assert model.b_eq.shape == (6 * horizon,)
    assert model.A_L0.shape == (6 * horizon, 1)
    assert model.A_Lt.shape == (6 * horizon, horizon)
    assert model.A_x.shape == (6 * horizon, 2 * horizon)
    assert model.A_B.shape == (6 * horizon, horizon + 1)

    inequality_rows = model.b_ineq.shape[0]
    assert model.G_L0.shape[0] == inequality_rows
    assert model.G_Lt.shape[0] == inequality_rows
    assert model.G_x.shape[0] == inequality_rows
    assert model.G_B.shape[0] == inequality_rows
    assert model.G_hatb.shape[0] == inequality_rows


def test_optimal_control_lp_builds_full_decision_vector() -> None:
    """The LP assembly should use every control block and the first objective entry."""
    horizon = 2
    model = BatteryLPBuilder(
        horizon=horizon,
        efficiency=0.95,
        pcs_capacity=10.0,
        charge_rate=5.0,
        B_lower=2.0,
        B_upper=10.0,
        loss=0.1,
    ).assemble()
    pv = _vector([1.0, 2.0])
    load = _vector([3.0, 4.0])

    problem = optimal_control_lp(model, pv, load)

    expected_width = (
        model.A_L0.shape[1]
        + model.A_Lt.shape[1]
        + model.A_x.shape[1]
        + model.A_y.shape[1]
        + model.A_z.shape[1]
        + model.A_b.shape[1]
        + model.A_B.shape[1]
        + model.A_hatb.shape[1]
    )
    assert problem.c.shape == (expected_width,)
    assert float(problem.c[0]) == 1.0
    assert problem.c[1:].tolist() == [0.0] * (expected_width - 1)

    assert problem.A_eq.shape == (model.b_eq.shape[0], expected_width)
    assert problem.A_ineq.shape == (model.b_ineq.shape[0], expected_width)
    assert problem.constraint_eq_dim == model.b_eq.shape[0]
    assert problem.constraint_ineq_dim == model.b_ineq.shape[0]

    expected_b_eq = _to_vector(
        cast(Any, model.b_eq - (model.A_p @ pv) - (model.A_C @ load))
    )
    expected_b_ineq = _to_vector(
        cast(Any, model.b_ineq - (model.G_p @ pv) - (model.G_C @ load))
    )
    assert _allclose(problem.b_eq, expected_b_eq)
    assert _allclose(problem.b_ineq, expected_b_ineq)


def test_optimal_control_lp_rejects_wrong_pv_length() -> None:
    """A wrong PV vector length should fail before sparse matmul."""
    model = BatteryLPBuilder(
        horizon=2,
        efficiency=0.95,
        pcs_capacity=10.0,
        charge_rate=5.0,
        B_lower=2.0,
        B_upper=10.0,
        loss=0.1,
    ).assemble()

    with pytest.raises(ValueError, match="pv must have length 2"):
        optimal_control_lp(
            model,
            pv=_vector([1.0]),
            load=_vector([3.0, 4.0]),
        )


def test_optimal_control_lp_rejects_wrong_load_length() -> None:
    """A wrong load vector length should fail before sparse matmul."""
    model = BatteryLPBuilder(
        horizon=2,
        efficiency=0.95,
        pcs_capacity=10.0,
        charge_rate=5.0,
        B_lower=2.0,
        B_upper=10.0,
        loss=0.1,
    ).assemble()

    with pytest.raises(ValueError, match="load must have length 2"):
        optimal_control_lp(
            model,
            pv=_vector([1.0, 2.0]),
            load=_vector([3.0]),
        )
