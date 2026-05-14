# type: ignore
# @dependency-start
# responsibility Configures local JAX dtype defaults for model smoke runs.
# upstream implementation ../../../pyproject.toml declares Python package configuration.
# downstream implementation LPproblem.py and model modules use JAX arrays.
# @dependency-end
import jax
from jax import numpy as jnp

DEFAULT_DTYPE = jnp.float32


def enable_x64() -> None:
    """Enable float64 support for local smoke runs."""
    jax.config.update("jax_enable_x64", True)
