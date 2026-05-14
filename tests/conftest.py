# @dependency-start
# responsibility Configures pytest runtime defaults.
# upstream implementation ../python/docomo_bt_management/dsl/primitives.py uses JAX numerics.
# downstream implementation ./dsl/test_primitives.py tests high-order DSL finite differences.
# @dependency-end
"""Pytest runtime configuration."""

from __future__ import annotations

import os

os.environ.setdefault("JAX_ENABLE_X64", "True")
os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")
