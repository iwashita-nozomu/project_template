# @dependency-start
# responsibility Exposes the public DSL API.
# upstream implementation ./primitives.py defines the DSL primitives.
# downstream implementation ../../../jupyter/test_primitive.ipynb exercises the public DSL surface.
# @dependency-end
"""Public DSL surface for function discretization."""

from .primitives import D, DiscretizationRequest, discretization

__all__ = [
    "D",
    "DiscretizationRequest",
    "discretization",
]
