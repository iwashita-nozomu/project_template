"""Assemble the battery-control LP from block matrices and exogenous series."""

from __future__ import annotations

from jax import numpy as jnp
from jax_util.base import Vector
from jax_util.base.linearoperator import LinOp, hstack_linops

from .battery_lp_builder import BlockMatricesSchoolmodel
from .lp_protocol import LPproblem


def optimal_control_lp(
    model: BlockMatricesSchoolmodel,
    pv: Vector,
    load: Vector,
) -> LPproblem:
    """Build the full LP for one PV/load scenario."""
    if int(pv.shape[0]) != model.A_p.shape[1]:
        raise ValueError(f"pv must have length {model.A_p.shape[1]}, got {pv.shape[0]}.")
    if int(load.shape[0]) != model.A_C.shape[1]:
        raise ValueError(
            f"load must have length {model.A_C.shape[1]}, got {load.shape[0]}."
        )

    objective_width = (
        model.A_L0.shape[1]
        + model.A_Lt.shape[1]
        + model.A_x.shape[1]
        + model.A_y.shape[1]
        + model.A_z.shape[1]
        + model.A_b.shape[1]
        + model.A_B.shape[1]
        + model.A_hatb.shape[1]
    )
    objective: Vector = jnp.zeros((objective_width,), dtype=model.dtype)
    objective = objective.at[0].set(1.0)

    equality_blocks = [
        model.A_L0,
        model.A_Lt,
        model.A_x,
        model.A_y,
        model.A_z,
        model.A_b,
        model.A_B,
        model.A_hatb,
    ]
    equality_operator = hstack_linops(
        [
            LinOp(
                lambda vector, dense_block=dense_block: vector @ dense_block.T,
                shape=block.shape,
            )
            for block in equality_blocks
            for dense_block in [
                jnp.asarray(block.todense(), dtype=model.dtype)
            ]
        ]
    )
    equality_rhs: Vector = jnp.asarray(
        model.b_eq - (model.A_p @ pv) - (model.A_C @ load),
        dtype=model.dtype,
    )

    inequality_blocks = [
        model.G_L0,
        model.G_Lt,
        model.G_x,
        model.G_y,
        model.G_z,
        model.G_b,
        model.G_B,
        model.G_hatb,
    ]
    inequality_operator = hstack_linops(
        [
            LinOp(
                lambda vector, dense_block=dense_block: vector @ dense_block.T,
                shape=block.shape,
            )
            for block in inequality_blocks
            for dense_block in [
                jnp.asarray(block.todense(), dtype=model.dtype)
            ]
        ]
    )
    inequality_rhs: Vector = jnp.asarray(
        model.b_ineq - (model.G_p @ pv) - (model.G_C @ load),
        dtype=model.dtype,
    )

    return LPproblem(
        c=objective,
        A_eq=equality_operator,
        b_eq=equality_rhs,
        A_ineq=inequality_operator,
        b_ineq=inequality_rhs,
    )
