# @dependency-start
# responsibility Provides a standalone jax_util algorithm-module shaped battery LP block assembler draft.
# upstream design ../../../notes/knowledge/imported_battery_lp_model_analysis.md documents battery LP formulation
# upstream implementation ./_env.py provides the repository default dtype
# upstream implementation ../../../docker/requirements.txt declares the jax_util algorithm module dependency
# @dependency-end
"""Standalone battery LP block assembler shaped as a jax_util algorithm module."""
from __future__ import annotations

import equinox as eqx
from jax import numpy as jnp
from jax.experimental import sparse as jsparse
from jax.typing import DTypeLike
from jax_util.base import Vector
from jax_util.base import algorithm_module_protocol as amp
from jaxtyping import Array

from ._env import DEFAULT_DTYPE

Z_MODE_BLOCKS = 7
EQUALITY_BLOCKS = 6
STATE_EQUATION_BLOCK = 3
DISCHARGE_SUM_BLOCK = 4
CHARGE_SUM_BLOCK = 5
Z_B_OFFSET_BLOCK = 1
M_HAT_OFFSET_BLOCK = 2
M_A_OFFSET_BLOCK = 3
M_P_OFFSET_BLOCK = 4
R_HAT_OFFSET_BLOCK = 5
R_C_OFFSET_BLOCK = 6


class InitializeConfig(amp.InitializeConfig):
    """Configuration for one battery LP block assembler."""

    horizon: int = eqx.field(static=True)
    efficiency: float = eqx.field(static=True)
    pcs_capacity: float = eqx.field(static=True)
    charge_rate: float = eqx.field(static=True)
    B_lower: float = eqx.field(static=True)
    B_upper: float = eqx.field(static=True)
    loss: float = eqx.field(static=True)
    dtype_name: str = eqx.field(static=True, default=jnp.dtype(DEFAULT_DTYPE).name)


class SolveConfig(amp.SolveConfig):
    """Runtime configuration for one battery LP assembly call."""


class Problem(amp.Problem):
    """Solve-time problem placeholder for parameter-free block assembly."""


class State(amp.State):
    """Warm-start state placeholder for stateless block assembly."""


class Info(amp.Info):
    """Diagnostics returned with assembled battery LP blocks."""

    horizon: int = eqx.field(static=True)
    equality_rows: int = eqx.field(static=True)
    inequality_rows: int = eqx.field(static=True)


class TripletBuilder:
    """Utility to collect triplets and emit a BCOO matrix."""

    def __init__(self) -> None:
        """Initialize empty triplet storage."""
        self.rows: list[int] = []
        self.cols: list[int] = []
        self.data: list[float] = []

    def add(self, row: int, col: int, value: float) -> None:
        """Append one sparse entry."""
        self.rows.append(int(row))
        self.cols.append(int(col))
        self.data.append(float(value))

    def to_bcoo(self, shape: tuple[int, int], dtype: DTypeLike = DEFAULT_DTYPE) -> jsparse.BCOO:
        """Materialize the collected triplets as a BCOO matrix."""
        if not self.data:
            return jsparse.BCOO(
                (jnp.zeros((0,), dtype=dtype), jnp.zeros((0, 2), dtype=jnp.int32)),
                shape=shape,
            )
        data: Array = jnp.asarray(self.data, dtype=dtype)
        rows = jnp.asarray(self.rows, dtype=jnp.int32)
        cols = jnp.asarray(self.cols, dtype=jnp.int32)
        indices: Array = jnp.stack((rows, cols), axis=1)
        return jsparse.BCOO((data, indices), shape=shape)


class Answer(amp.Answer):
    """Block-structured LP matrices returned by one assembly call."""

    # Equality blocks (6N rows)
    dtype: DTypeLike = eqx.field(static=True)
    A_L0: jsparse.BCOO
    A_Lt: jsparse.BCOO
    A_x: jsparse.BCOO
    A_y: jsparse.BCOO
    A_z: jsparse.BCOO
    A_b: jsparse.BCOO
    A_B: jsparse.BCOO
    A_p: jsparse.BCOO
    A_C: jsparse.BCOO
    A_hatb: jsparse.BCOO
    b_eq: Vector
    # Inequality blocks (m rows)
    G_L0: jsparse.BCOO
    G_Lt: jsparse.BCOO
    G_x: jsparse.BCOO
    G_y: jsparse.BCOO
    G_z: jsparse.BCOO
    G_b: jsparse.BCOO
    G_B: jsparse.BCOO
    G_p: jsparse.BCOO
    G_C: jsparse.BCOO
    G_hatb: jsparse.BCOO
    b_ineq: Vector


class Algorithm(amp.Algorithm[Problem, State, SolveConfig, Answer, Info]):
    """Callable battery LP block assembler returned by ``initialize``."""

    N: int = eqx.field(static=True)
    eff: float = eqx.field(static=True)
    pcs: float = eqx.field(static=True)
    charge: float = eqx.field(static=True)
    B_lower: float = eqx.field(static=True)
    B_upper: float = eqx.field(static=True)
    loss: float = eqx.field(static=True)
    dtype: DTypeLike = eqx.field(static=True)
    M_x: float = eqx.field(static=True)
    M_y: float = eqx.field(static=True)
    M_b: float = eqx.field(static=True)
    M_hat: float = eqx.field(static=True)
    M_a1: float = eqx.field(static=True)
    M_a2: float = eqx.field(static=True)
    M_a3: float = eqx.field(static=True)
    M_c1: float = eqx.field(static=True)
    M_c2: float = eqx.field(static=True)

    def __call__(
        self,
        problem: Problem,
        state: State,
        runtime_config: SolveConfig,
        /,
    ) -> tuple[Answer, State, Info]:
        """Assemble block matrices and return the unchanged stateless state."""
        _ = problem, runtime_config
        blocks = self._build_answer()
        return (
            blocks,
            state,
            Info(
                horizon=self.N,
                equality_rows=int(blocks.b_eq.shape[0]),
                inequality_rows=int(blocks.b_ineq.shape[0]),
            ),
        )

    def _build_answer(self) -> Answer:
        """Assemble the full equality and inequality LP block matrices."""
        N = self.N
        dtype = self.dtype

        dim_L0 = 1
        dim_Lt = N
        dim_x = 2 * N
        dim_y = 2 * N
        dim_z = Z_MODE_BLOCKS * N
        dim_b = 2 * N
        dim_B = N + 1
        dim_hatb = 2 * N

        eq_rows = EQUALITY_BLOCKS * N

        def eq_block(block_index: int, time_index: int) -> int:
            """Map one block/time pair to a row index."""
            return block_index * N + time_index

        b_eq = [0.0] * eq_rows

        # triplet builders
        AL0 = TripletBuilder()
        ALt = TripletBuilder()
        Ax = TripletBuilder()
        Ay = TripletBuilder()
        Az = TripletBuilder()
        Ab = TripletBuilder()
        AB = TripletBuilder()
        Ap = TripletBuilder()
        AC = TripletBuilder()
        Ahat = TripletBuilder()

        # 0) Lt definition
        for i in range(N):
            row = eq_block(0, i)
            ALt.add(row, i, 1.0)
            Ay.add(row, i, 1.0)
            Ay.add(row, N + i, -1.0)
            AC.add(row, i, -1.0)

        # 1) Efficiency
        for i in range(N):
            row = eq_block(1, i)
            Ax.add(row, i, -self.eff)
            Ax.add(row, N + i, 1.0 / self.eff)
            Ay.add(row, i, 1.0)
            Ay.add(row, N + i, -1.0)

        # 2) Flow
        for i in range(N):
            row = eq_block(2, i)
            Ax.add(row, i, 1.0)
            Ax.add(row, N + i, -1.0)
            Ab.add(row, i, -1.0)
            Ab.add(row, N + i, 1.0)
            Ap.add(row, i, -1.0)

        # 3) State
        for i in range(N):
            row = eq_block(STATE_EQUATION_BLOCK, i)
            AB.add(row, i, 1.0)
            AB.add(row, i + 1, -1.0)
            Ab.add(row, i, -1.0)
            Ab.add(row, N + i, 1.0)
            b_eq[row] = self.loss

        # 4) Discharge sum
        off_zb = Z_B_OFFSET_BLOCK * N
        off_mhat = M_HAT_OFFSET_BLOCK * N
        off_ma = M_A_OFFSET_BLOCK * N
        off_mp = M_P_OFFSET_BLOCK * N
        for i in range(N):
            row = eq_block(DISCHARGE_SUM_BLOCK, i)
            Az.add(row, off_zb + i, 1.0)
            Az.add(row, off_mhat + i, -1.0)
            Az.add(row, off_ma + i, -1.0)
            Az.add(row, off_mp + i, -1.0)

        # 5) Charge sum
        off_rhat = R_HAT_OFFSET_BLOCK * N
        off_rc = R_C_OFFSET_BLOCK * N
        for i in range(N):
            row = eq_block(CHARGE_SUM_BLOCK, i)
            Az.add(row, off_rhat + i, 1.0)
            Az.add(row, off_rc + i, 1.0)
            Az.add(row, off_zb + i, 1.0)
            b_eq[row] = 1.0

        # Inequalities
        GL0 = TripletBuilder()
        GLt = TripletBuilder()
        Gx = TripletBuilder()
        Gy = TripletBuilder()
        Gz = TripletBuilder()
        Gb = TripletBuilder()
        GB = TripletBuilder()
        Gp = TripletBuilder()
        GC = TripletBuilder()
        Ghat = TripletBuilder()

        b_ineq_vals: list[float] = []
        ineq_row = 0

        def current_row() -> int:
            return ineq_row

        def push(value: float) -> None:
            nonlocal ineq_row
            b_ineq_vals.append(float(value))
            ineq_row += 1

        # (a) PCS direction
        for i in range(N):
            row = current_row()
            Gx.add(row, i, 1.0)
            Gz.add(row, i, -self.M_x)
            push(0.0)

            row = current_row()
            Gx.add(row, N + i, 1.0)
            Gz.add(row, i, self.M_x)
            push(self.M_x)

            row = current_row()
            Gy.add(row, i, 1.0)
            Gz.add(row, i, -self.M_y)
            push(0.0)

            row = current_row()
            Gy.add(row, N + i, 1.0)
            Gz.add(row, i, self.M_y)
            push(self.M_y)

        # (b) Battery direction + capacity caps
        for i in range(N):
            row = current_row()
            Gb.add(row, i, 1.0)
            Gz.add(row, off_zb + i, -self.M_b)
            push(0.0)

            row = current_row()
            Gb.add(row, N + i, 1.0)
            Gz.add(row, off_zb + i, self.M_b)
            push(self.M_b)

            # 注: ここはビッグM + バイナリ(z_b) による「同時充放電の禁止」を補強する冗長制約です。
            #     元のモデル（z_b を含む）では論理的に含意されますが、
            #     FM 縮約で z/b を消す際に数値丸め・冗長削除が入ると、この種の結合制約が
            #     弱くなったり消えたりして、緩みとして現れることがあります。
            #     そのため、(b_pos + b_neg <= charge) を明示的に追加しておきます。
            row = current_row()
            Gb.add(row, i, 1.0)
            Gb.add(row, N + i, 1.0)
            push(self.charge)

            # row = current_row()
            # Gb.add(row, i, 1.0)
            # push(self.charge)

            # row = current_row()
            # Gb.add(row, N + i, 1.0)
            # push(self.charge)

            row = current_row()
            Ghat.add(row, i, 1.0)
            Gz.add(row, off_mhat + i, -self.M_hat)
            push(0.0)

            row = current_row()
            Ghat.add(row, N + i, 1.0)
            Gz.add(row, off_rhat + i, -self.M_hat)
            # 注: ここは hatb_neg <= M_hat * z_rhat を表したいので、右辺は 0 が正しいです。
            #     右辺を M_hat にすると z_rhat=0 でも hatb_neg <= M_hat が許され、
            #     (hatb_pos, hatb_neg) の排他が弱くなって縮約後の緩みとして現れやすくなります。
            push(0.0)

            row = current_row()
            Ghat.add(row, i, 1.0)
            push(self.charge)

            row = current_row()
            Ghat.add(row, N + i, 1.0)
            push(self.charge)

            # 注: hatb も同様に、正負成分の合計に上限を入れておくと縮約後の緩みを抑えられます。
            row = current_row()
            Ghat.add(row, i, 1.0)
            Ghat.add(row, N + i, 1.0)
            push(self.charge)

        # (c) SoC bounds
        for i in range(N + 1):
            row = current_row()
            GB.add(row, i, 1.0)
            push(self.B_upper)

            row = current_row()
            GB.add(row, i, -1.0)
            push(-self.B_lower)

        # (d) Discharge min linearization
        for i in range(N):
            row = current_row()
            Gb.add(row, i, 1.0)
            Ghat.add(row, i, -1.0)
            push(0.0)

            row = current_row()
            Gz.add(row, off_mhat + i, self.M_a1)
            Gb.add(row, i, -1.0)
            Ghat.add(row, i, 1.0)
            push(self.M_a1)

            row = current_row()
            Gb.add(row, i, 1.0)
            GB.add(row, i, -1.0)
            push(-self.loss - self.B_lower)

            row = current_row()
            Gz.add(row, off_ma + i, self.M_a2)
            Gb.add(row, i, -1.0)
            GB.add(row, i, 1.0)
            push(self.loss + self.B_lower + self.M_a2)

            row = current_row()
            Gb.add(row, i, 1.0)
            Gp.add(row, i, 1.0)
            push(self.pcs)

            row = current_row()
            Gz.add(row, off_mp + i, self.M_a3)
            Gb.add(row, i, -1.0)
            Gp.add(row, i, -1.0)
            push(-self.pcs + self.M_a3)

        # (e) Charge min linearization
        for i in range(N):
            row = current_row()
            Ghat.add(row, N + i, -1.0)
            Gb.add(row, N + i, 1.0)
            push(0.0)

            row = current_row()
            Gz.add(row, off_rhat + i, self.M_c1)
            Gb.add(row, N + i, -1.0)
            Ghat.add(row, N + i, 1.0)
            push(self.M_c1)

            row = current_row()
            Gb.add(row, N + i, 1.0)
            GB.add(row, i, 1.0)
            push(self.B_upper + self.loss)

            row = current_row()
            Gz.add(row, off_rc + i, self.M_c2)
            Gb.add(row, N + i, -1.0)
            GB.add(row, i, -1.0)
            push(-self.B_upper - self.loss + self.M_c2)

        # (f) Peak via L
        for i in range(N):
            row = current_row()
            GL0.add(row, 0, -1.0)
            GLt.add(row, i, 1.0)
            push(0.0)

        # (g) Absolute caps for x, y
        for i in range(N):
            row = current_row()
            Gy.add(row, i, 1.0)
            Gy.add(row, N + i, 1.0)
            push(self.pcs)

            row = current_row()
            Gx.add(row, i, 1.0)
            Gx.add(row, N + i, 1.0)
            push(self.pcs)

        # (h) z bounds
        for i in range(N):
            row = current_row()
            Gz.add(row, i, -1.0)
            push(0.0)
            row = current_row()
            Gz.add(row, i, 1.0)
            push(1.0)

            row = current_row()
            Gz.add(row, off_zb + i, -1.0)
            push(0.0)
            row = current_row()
            Gz.add(row, off_zb + i, 1.0)
            push(1.0)

            row = current_row()
            Gz.add(row, off_mhat + i, -1.0)
            push(0.0)
            row = current_row()
            Gz.add(row, off_mhat + i, 1.0)
            push(1.0)

            row = current_row()
            Gz.add(row, off_ma + i, -1.0)
            push(0.0)
            row = current_row()
            Gz.add(row, off_ma + i, 1.0)
            push(1.0)

            row = current_row()
            Gz.add(row, off_mp + i, -1.0)
            push(0.0)
            row = current_row()
            Gz.add(row, off_mp + i, 1.0)
            push(1.0)

            row = current_row()
            Gz.add(row, off_rhat + i, -1.0)
            push(0.0)
            row = current_row()
            Gz.add(row, off_rhat + i, 1.0)
            push(1.0)

            row = current_row()
            Gz.add(row, off_rc + i, -1.0)
            push(0.0)
            row = current_row()
            Gz.add(row, off_rc + i, 1.0)
            push(1.0)

        # (i) Non-negativity
        row = current_row()
        GL0.add(row, 0, -1.0)
        push(0.0)

        for i in range(N):
            row = current_row()
            GLt.add(row, i, -1.0)
            push(0.0)

        for i in range(2 * N):
            row = current_row()
            Gx.add(row, i, -1.0)
            push(0.0)

        for i in range(2 * N):
            row = current_row()
            Gy.add(row, i, -1.0)
            push(0.0)

        for i in range(2 * N):
            row = current_row()
            Gb.add(row, i, -1.0)
            push(0.0)

        for i in range(N + 1):
            row = current_row()
            GB.add(row, i, -1.0)
            push(0.0)

        m_ineq = ineq_row
        b_ineq = jnp.asarray(b_ineq_vals, dtype=dtype)

        def make(builder: TripletBuilder, rows: int, cols: int) -> jsparse.BCOO:
            return builder.to_bcoo((rows, cols), dtype)

        return Answer(
            dtype=dtype,
            A_L0=make(AL0, eq_rows, dim_L0),
            A_Lt=make(ALt, eq_rows, dim_Lt),
            A_x=make(Ax, eq_rows, dim_x),
            A_y=make(Ay, eq_rows, dim_y),
            A_z=make(Az, eq_rows, dim_z),
            A_b=make(Ab, eq_rows, dim_b),
            A_B=make(AB, eq_rows, dim_B),
            A_p=make(Ap, eq_rows, N),
            A_C=make(AC, eq_rows, N),
            A_hatb=make(Ahat, eq_rows, dim_hatb),
            b_eq=jnp.asarray(b_eq, dtype=dtype),
            G_L0=make(GL0, m_ineq, dim_L0),
            G_Lt=make(GLt, m_ineq, dim_Lt),
            G_x=make(Gx, m_ineq, dim_x),
            G_y=make(Gy, m_ineq, dim_y),
            G_z=make(Gz, m_ineq, dim_z),
            G_b=make(Gb, m_ineq, dim_b),
            G_B=make(GB, m_ineq, dim_B),
            G_p=make(Gp, m_ineq, N),
            G_C=make(GC, m_ineq, N),
            G_hatb=make(Ghat, m_ineq, dim_hatb),
            b_ineq=jnp.asarray(b_ineq, dtype=dtype),
        )


def initialize(config: InitializeConfig) -> tuple[Algorithm, State]:
    """Build one battery LP assembler and its stateless initial state."""
    dtype = jnp.dtype(config.dtype_name)
    pcs = float(config.pcs_capacity)
    charge = float(config.charge_rate)
    battery_span = float(config.B_upper) - float(config.B_lower)
    M_hat = charge
    M_a2 = battery_span + float(config.loss)
    return (
        Algorithm(
            N=int(config.horizon),
            eff=float(config.efficiency),
            pcs=pcs,
            charge=charge,
            B_lower=float(config.B_lower),
            B_upper=float(config.B_upper),
            loss=float(config.loss),
            dtype=dtype,
            M_x=pcs,
            M_y=pcs,
            M_b=charge,
            M_hat=M_hat,
            M_a1=M_hat,
            M_a2=M_a2,
            M_a3=2.0 * pcs,
            M_c1=M_hat,
            M_c2=M_a2,
        ),
        State(),
    )


__all__ = [
    "InitializeConfig",
    "SolveConfig",
    "Problem",
    "State",
    "Answer",
    "Info",
    "Algorithm",
    "initialize",
]
