"""Minimal PDIPM smoke run for the battery LP assembly."""

from __future__ import annotations

import os

os.environ["JAX_UTIL_DEBUG"] = "false"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

from jax import numpy as jnp
from jax_util.base import MaxRelativeRayleighResidualCriterion, ResidualNormConvergenceCriterion
from jax_util.optimizers import pdipm
from jax_util.solvers import kkt, lobpcg, minres

from .model._env import enable_x64
from .model.battery_lp_builder import BatteryLPBuilder
from .model.LPproblem import optimal_control_lp

enable_x64()

def main() -> None:
    """Run one tiny PDIPM solve on the assembled battery LP."""
    model = BatteryLPBuilder(2, 0.95, 10.0, 5.0, 2.0, 10.0, 0.1, dtype=jnp.float64).assemble()
    pv = jnp.asarray([1.0, 2.0], dtype=jnp.float64)
    load = jnp.asarray([3.0, 4.0], dtype=jnp.float64)
    problem = optimal_control_lp(model, pv, load)
    state = pdipm.initialize(
        pdipm.PDIPMInitializeConfig(
            n_primal=problem.variable_dim,
            n_dual_eq=problem.constraint_eq_dim,
            n_dual_ineq=problem.constraint_ineq_dim,
            r_Hv=1,
            r_Sv=1,
            dtype=jnp.float64,
        )
    )
    value, next_state, info = pdipm.solve(
        f_opt=problem.objective,
        c_eq=problem.constraint_eq,
        c_ineq=problem.constraint_ineq,
        optimizer_state=state,
        n_primal=problem.variable_dim,
        m_eq=problem.constraint_eq_dim,
        m_ineq=problem.constraint_ineq_dim,
        solve_config=pdipm.PDIPMSolveConfig(
            max_steps=10,
            ipm_atol=jnp.asarray(1.0e-2, dtype=jnp.float64),
            kkt_solve=kkt.KKTSolveConfig(
                solver_solve=minres.MINRESSolveConfig(
                    stopping=ResidualNormConvergenceCriterion(
                        maxiter=500,
                        rtol=jnp.asarray(1.0e-2, dtype=jnp.float64),
                        reference="rhs",
                    )
                ),
                h_update_solve=lobpcg.LOBPCGSolveConfig(
                    stopping=MaxRelativeRayleighResidualCriterion(
                        maxiter=20,
                        rtol=jnp.asarray(1.0e-4, dtype=jnp.float64),
                    )
                ),
                s_update_solve=lobpcg.LOBPCGSolveConfig(
                    stopping=MaxRelativeRayleighResidualCriterion(
                        maxiter=10,
                        rtol=jnp.asarray(1.0e-4, dtype=jnp.float64),
                    )
                ),
            ),
        ),
    )
    print(
        float(value),
        int(info["step_count"]),
        float(info["prim_res_final"]),
        float(info["mu_final"]),
        next_state.x.shape,
    )


if __name__ == "__main__":
    main()
