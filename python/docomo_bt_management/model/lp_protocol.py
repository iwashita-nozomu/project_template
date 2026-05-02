"""Small LP container matching the optimizer protocol surface used in this repo."""

from __future__ import annotations

from collections.abc import Callable

from jax_util.base import Scalar, Vector
from jax_util.base.linearoperator import LinearOperator


class LPproblem:
    """Represent a linear program via operators and callable constraints."""

    c: Vector
    A_eq: LinearOperator
    b_eq: Vector
    A_ineq: LinearOperator
    b_ineq: Vector
    objective: Callable[[Vector], Scalar]
    constraint_eq: Callable[[Vector], Vector]
    constraint_ineq: Callable[[Vector], Vector]
    variable_dim: int
    constraint_eq_dim: int
    constraint_ineq_dim: int

    def __init__(
        self,
        c: Vector,
        A_eq: LinearOperator,
        b_eq: Vector,
        A_ineq: LinearOperator,
        b_ineq: Vector,
    ) -> None:
        """Store one LP in operator form."""
        self.c = c
        self.A_eq = A_eq
        self.b_eq = b_eq
        self.A_ineq = A_ineq
        self.b_ineq = b_ineq

        self.objective = lambda x: x @ self.c
        self.constraint_eq = lambda x: (self.A_eq @ x) - self.b_eq
        self.constraint_ineq = lambda x: (self.A_ineq @ x) - self.b_ineq
        self.variable_dim = int(self.c.shape[0])
        self.constraint_eq_dim = int(self.b_eq.shape[0])
        self.constraint_ineq_dim = int(self.b_ineq.shape[0])
