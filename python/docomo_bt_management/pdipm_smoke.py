# @dependency-start
# responsibility Runs a minimal smoke solve for the battery LP assembly path.
# upstream implementation ./model/battery_lp_builder.py builds battery LP block answers
# upstream implementation ./model/LPproblem.py assembles solver-facing LP problems
# upstream implementation ../../docker/requirements.txt declares jax_util solver dependencies
# @dependency-end
"""Minimal PDIPM smoke run for the battery LP assembly."""

from __future__ import annotations

import os

os.environ["JAX_UTIL_DEBUG"] = "false"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

from jax import numpy as jnp
from jax_util.base import ResidualNormConvergenceCriterion
from jax_util.optimizers import pdipm
from jax_util.solvers import _preconditioners, kkt, minres

from .model import battery_lp_builder
from .model._env import enable_x64
from .model.LPproblem import optimal_control_lp

enable_x64()

SMOKE_HORIZON = 2
SMOKE_EFFICIENCY = 0.95
SMOKE_PCS_CAPACITY = 10.0
SMOKE_CHARGE_RATE = 5.0
SMOKE_B_LOWER = 2.0
SMOKE_B_UPPER = 10.0
SMOKE_LOSS = 0.1
SMOKE_PV = (1.0, 2.0)
SMOKE_LOAD = (3.0, 4.0)
PDIPM_MAX_STEPS = 10
PDIPM_IPM_ATOL = "1e-2"
MINRES_MAXITER = 500
MINRES_RTOL = "1e-2"


def _battery_lp_blocks() -> battery_lp_builder.Answer:
    """Build the tiny smoke-test battery LP block answer."""
    algorithm, state = battery_lp_builder.initialize(
        battery_lp_builder.InitializeConfig(
            horizon=SMOKE_HORIZON,
            efficiency=SMOKE_EFFICIENCY,
            pcs_capacity=SMOKE_PCS_CAPACITY,
            charge_rate=SMOKE_CHARGE_RATE,
            B_lower=SMOKE_B_LOWER,
            B_upper=SMOKE_B_UPPER,
            loss=SMOKE_LOSS,
            dtype_name=jnp.dtype(jnp.float64).name,
        )
    )
    answer, _, _ = algorithm(
        battery_lp_builder.Problem(),
        state,
        battery_lp_builder.SolveConfig(),
    )
    return answer


def main() -> None:
    """Run one tiny PDIPM solve on the assembled battery LP."""
    model = _battery_lp_blocks()
    pv = jnp.asarray(SMOKE_PV, dtype=jnp.float64)
    load = jnp.asarray(SMOKE_LOAD, dtype=jnp.float64)
    problem = optimal_control_lp(model, pv, load)
    dtype_name = jnp.dtype(jnp.float64).name
    kkt_initialize = kkt.InitializeConfig(
        n_primal=problem.variable_dim,
        n_dual=problem.constraint_eq_dim,
        solver_initialize=minres.InitializeConfig(
            dimension=problem.variable_dim + problem.constraint_eq_dim,
            dtype_name=dtype_name,
        ),
        h_preconditioner_initialize=_preconditioners.InitializeConfig.identity(),
        s_preconditioner_initialize=_preconditioners.InitializeConfig.identity(),
        dtype_name=dtype_name,
    )
    algorithm, state = pdipm.initialize(
        pdipm.InitializeConfig(
            n_primal=problem.variable_dim,
            n_dual_eq=problem.constraint_eq_dim,
            n_dual_ineq=problem.constraint_ineq_dim,
            kkt_initialize=kkt_initialize,
            dtype_name=dtype_name,
        )
    )
    answer, next_state, info = algorithm(
        pdipm.Problem(
            f_opt=problem.objective,
            c_eq=problem.constraint_eq,
            c_ineq=problem.constraint_ineq,
        ),
        state,
        pdipm.SolveConfig(
            max_steps=PDIPM_MAX_STEPS,
            ipm_atol=PDIPM_IPM_ATOL,
            kkt_solve=kkt.SolveConfig(
                solver_solve=minres.SolveConfig(
                    stopping=ResidualNormConvergenceCriterion(
                        maxiter=MINRES_MAXITER,
                        rtol=MINRES_RTOL,
                        reference="rhs",
                    )
                ),
                h_preconditioner_solve=_preconditioners.SolveConfig.identity(),
                s_preconditioner_solve=_preconditioners.SolveConfig.identity(),
            ),
        ),
    )
    print(
        float(answer.objective_value),
        int(info.step_count),
        float(info.prim_res_final),
        float(info.mu_final),
        next_state.x.shape,
    )


if __name__ == "__main__":
    main()
