# @dependency-start
# responsibility Describes the public DSL package exports.
# upstream implementation ./__init__.py re-exports the runtime DSL surface.
# upstream implementation ./primitives.pyi defines the primitive type contracts.
# @dependency-end
"""Type stubs for the public DSL package."""

from .primitives import D as D
from .primitives import DiscretizationRequest as DiscretizationRequest
from .primitives import discretization as discretization

__all__: tuple[str, ...]
