# @dependency-start
# responsibility Drafts the calculation algorithm-module integration surface.
# upstream implementation ./lp_protocol.py defines the local LP problem container
# upstream implementation ../../../docker/requirements.txt declares jax_util algorithm dependencies
# @dependency-end
"""Draft calculation algorithm module integration surface."""

from __future__ import annotations

from jax_util import pdipm
from jax_util.base import algorithm_module_protocol as amp

from .lp_protocol import LPproblem


class InitializeConfig(amp.InitializeConfig):
    """Configuration for the draft calculation module."""

    pdipm_config: pdipm.InitializeConfig


class Problem(amp.Problem):
    """Calculation problem wrapping one assembled LP."""

    lp_problem: LPproblem
