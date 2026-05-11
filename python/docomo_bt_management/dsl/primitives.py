from __future__ import annotations

from ast import Call
from typing import Literal,Generic, TypeVar, runtime_checkable,Dict , Callable

# from jax_util.base import algorithm_module_protocol as amp

from dataclasses import dataclass

import inspect

import jax

import jax.numpy as jnp
from jaxtyping import DTypeLike

ArrayLike = TypeVar("ArrayLike")

ArgName = Literal["t"]

DTypeLike = TypeVar("DTypeLike", bound=jnp.dtype)

def discretization(
    function: Callable[..., ArrayLike],
    argname: ArgName,
    num_points: int,
    domain: tuple[float, float],
    *,
    dtype: DTypeLike = jnp.float64,
):

    if num_points <= 0:
        raise ValueError("num_points must be a positive integer.")
    if len(domain) != 2:

        raise ValueError("domain must be a tuple of (start, end).")
    params = inspect.signature(function).parameters    
    if argname not in params:
        print(f"Function parameters: {params}")
        return 

    start, end = domain
    if start >= end:
        raise ValueError("domain start must be less than end.")
    

    # 離散化列に従ってtを生成
    
    t_values = jnp.linspace(start, end, num_points + 1) #　境界の点も含めるためにnum_points + 1
    
    # jnp.arrayに関数を保持

    def discretized_function(*args: ArrayLike, **kwargs: ArrayLike) -> ArrayLike:
        if argname not in kwargs:
            return function(*args, **kwargs)

        return jax.vmap(lambda t: function(*args, **kwargs, **{argname: t}))(t_values)
    
    return discretized_function
     
    
