# type: ignore
import jax
from jax import numpy as jnp

DEFAULT_DTYPE = jnp.float32


def enable_x64() -> None:
    """Enable float64 support for local smoke runs."""
    jax.config.update("jax_enable_x64", True)
