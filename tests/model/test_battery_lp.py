# @dependency-start
# responsibility Tests battery LP block assembly and LP problem wiring.
# upstream implementation ../../python/docomo_bt_management/model/battery_lp_builder.py builds battery LP block answers
# upstream implementation ../../python/docomo_bt_management/model/LPproblem.py assembles solver-facing LP problems
# @dependency-end
"""Tests for battery LP block assembly and LP problem wiring."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import jax.numpy as jnp
import numpy as np
import pytest
from docomo_bt_management.model import battery_lp_builder
from docomo_bt_management.model.LPproblem import optimal_control_lp
from jax.typing import DTypeLike
from jax_util.base import Vector

SHAPE_HORIZON = 3
SHAPE_EFFICIENCY = 0.9
SHAPE_PCS_CAPACITY = 2.0
SHAPE_CHARGE_RATE = 1.5
SHAPE_B_LOWER = 0.0
SHAPE_B_UPPER = 4.0
SHAPE_LOSS = 0.01
EQUALITY_ROWS_PER_HORIZON = 6
SCALAR_BLOCK_WIDTH = 1
SIGNED_HORIZON_BLOCKS = 2
LP_HORIZON = 2
LP_EFFICIENCY = 0.95
LP_PCS_CAPACITY = 10.0
LP_CHARGE_RATE = 5.0
LP_B_LOWER = 2.0
LP_B_UPPER = 10.0
LP_LOSS = 0.1
PV_VALUES = [1.0, 2.0]
LOAD_VALUES = [3.0, 4.0]
WRONG_PV_VALUES = [1.0]
WRONG_LOAD_VALUES = [3.0]

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


def _build_battery_lp_blocks(
    *,
    horizon: int,
    efficiency: float,
    pcs_capacity: float,
    charge_rate: float,
    B_lower: float,
    B_upper: float,
    loss: float,
    dtype: DTypeLike = jnp.float32,
) -> battery_lp_builder.Answer:
    """Build battery LP blocks through the algorithm module interface."""
    algorithm, state = battery_lp_builder.initialize(
        battery_lp_builder.InitializeConfig(
            horizon=horizon,
            efficiency=efficiency,
            pcs_capacity=pcs_capacity,
            charge_rate=charge_rate,
            B_lower=B_lower,
            B_upper=B_upper,
            loss=loss,
            dtype_name=jnp.dtype(dtype).name,
        )
    )
    answer, _, _ = algorithm(
        battery_lp_builder.Problem(),
        state,
        battery_lp_builder.SolveConfig(),
    )
    return answer


def test_battery_lp_algorithm_module_keeps_block_shapes_consistent() -> None:
    """The algorithm module should emit consistent row counts and horizon widths."""
    model = _build_battery_lp_blocks(
        horizon=SHAPE_HORIZON,
        efficiency=SHAPE_EFFICIENCY,
        pcs_capacity=SHAPE_PCS_CAPACITY,
        charge_rate=SHAPE_CHARGE_RATE,
        B_lower=SHAPE_B_LOWER,
        B_upper=SHAPE_B_UPPER,
        loss=SHAPE_LOSS,
    )

    assert model.dtype == jnp.float32
    equality_rows = EQUALITY_ROWS_PER_HORIZON * SHAPE_HORIZON
    assert model.b_eq.shape == (equality_rows,)
    assert model.A_L0.shape == (equality_rows, SCALAR_BLOCK_WIDTH)
    assert model.A_Lt.shape == (equality_rows, SHAPE_HORIZON)
    assert model.A_x.shape == (equality_rows, SIGNED_HORIZON_BLOCKS * SHAPE_HORIZON)
    assert model.A_B.shape == (equality_rows, SHAPE_HORIZON + SCALAR_BLOCK_WIDTH)

    inequality_rows = model.b_ineq.shape[0]
    assert model.G_L0.shape[0] == inequality_rows
    assert model.G_Lt.shape[0] == inequality_rows
    assert model.G_x.shape[0] == inequality_rows
    assert model.G_B.shape[0] == inequality_rows
    assert model.G_hatb.shape[0] == inequality_rows


def test_optimal_control_lp_builds_full_decision_vector() -> None:
    """The LP assembly should use every control block and the first objective entry."""
    model = _build_battery_lp_blocks(
        horizon=LP_HORIZON,
        efficiency=LP_EFFICIENCY,
        pcs_capacity=LP_PCS_CAPACITY,
        charge_rate=LP_CHARGE_RATE,
        B_lower=LP_B_LOWER,
        B_upper=LP_B_UPPER,
        loss=LP_LOSS,
    )
    pv = _vector(PV_VALUES)
    load = _vector(LOAD_VALUES)

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
        cast(Vector, model.b_eq - (model.A_p @ pv) - (model.A_C @ load))
    )
    expected_b_ineq = _to_vector(
        cast(Vector, model.b_ineq - (model.G_p @ pv) - (model.G_C @ load))
    )
    assert _allclose(problem.b_eq, expected_b_eq)
    assert _allclose(problem.b_ineq, expected_b_ineq)


def test_optimal_control_lp_rejects_wrong_pv_length() -> None:
    """A wrong PV vector length should fail before sparse matmul."""
    model = _build_battery_lp_blocks(
        horizon=LP_HORIZON,
        efficiency=LP_EFFICIENCY,
        pcs_capacity=LP_PCS_CAPACITY,
        charge_rate=LP_CHARGE_RATE,
        B_lower=LP_B_LOWER,
        B_upper=LP_B_UPPER,
        loss=LP_LOSS,
    )

    with pytest.raises(ValueError, match="pv must have length 2"):
        optimal_control_lp(
            model,
            pv=_vector(WRONG_PV_VALUES),
            load=_vector(LOAD_VALUES),
        )


def test_optimal_control_lp_rejects_wrong_load_length() -> None:
    """A wrong load vector length should fail before sparse matmul."""
    model = _build_battery_lp_blocks(
        horizon=LP_HORIZON,
        efficiency=LP_EFFICIENCY,
        pcs_capacity=LP_PCS_CAPACITY,
        charge_rate=LP_CHARGE_RATE,
        B_lower=LP_B_LOWER,
        B_upper=LP_B_UPPER,
        loss=LP_LOSS,
    )

    with pytest.raises(ValueError, match="load must have length 2"):
        optimal_control_lp(
            model,
            pv=_vector(PV_VALUES),
            load=_vector(WRONG_LOAD_VALUES),
        )
