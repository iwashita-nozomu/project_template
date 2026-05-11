<!--
@dependency-start
responsibility Defines the design for discretizing functionals of continuous trajectories into finite-dimensional representations.
upstream implementation ../docker/requirements.txt declares JAX, Equinox, and jaxtyping dependencies available for implementation.
upstream implementation ../python/docomo_bt_management/model/calculate.py is the future calculation-module integration surface.
downstream implementation ../python/docomo_bt_management/model/calculate.py should host or call the first implementation slice.
@dependency-end
-->

# Functional Discretization Design

## Purpose

We want a reusable way to take a continuous expression such as

$$
f(t, x(t), \dot{x}(t), y(t), \dot{y}(t), u(t), \theta)
$$

and lower it to a finite-dimensional representation that can be evaluated by
JAX-based optimizers and solvers.

Metaprogramming is acceptable for the user-facing authoring layer. The stable
internal target is still a small, explicit lowering layer that treats a
finite-dimensional representation as an arbitrary JAX PyTree plus an
evaluation contract. Grids, bases, finite elements, splines, neural
parametrizations, and solver-defined latent states are all adapters behind that
contract. Multiple continuous variables are first-class; each variable can have
its own finite representation and derivative orders. Decorators, signature
inspection, operator-overloaded symbolic variables, and constrained tracing can
all be used to produce the internal lowering spec.

## Problem Shape

The continuous input is a named family of continuous variables

$$
\mathcal{V} = \{x, y, u, \ldots\}, \qquad
v_a : \Omega_a \to Y_a.
$$

The common ODE-style case has a shared time domain
`Omega_a = [t0, t1]`, but the design must also allow variables with different
domains or observation semantics, such as a trajectory `x(t)`, a control
`u(t)`, a static parameter field `p(s)`, or a boundary variable.

A functional can be one of two forms.

Pointwise form:

$$
r(t) = f(t, \operatorname{jet}(x)(t), \operatorname{jet}(y)(t), \operatorname{jet}(u)(t), \theta)
$$

Integral form:

$$
J[\mathcal{V}] = \int_{t_0}^{t_1} f(t, \operatorname{jet}(x)(t), \operatorname{jet}(y)(t), \operatorname{jet}(u)(t), \theta)\,dt.
$$

The finite-dimensional representation chooses one finite parameter object per
variable

$$
\mathbf{q} = \{q_x, q_y, q_u, \ldots\}, \qquad q_a \in Q_{h,a}
$$

where each `Q_{h,a}` is represented in code as a JAX PyTree with finite array
leaves. There is no requirement that any `q_a` is a flat vector, a basis
coefficient vector, or a grid-value vector. Different variables may use
different representations.

Each variable representation supplies an evaluation map for the requested jet
data:

$$
E_{h,a}(q_a, \rho_a) \to (v_a, Dv_a, \ldots, D^{k_a}v_a).
$$

Here `rho_a` is an observation request for variable `a`. Requests may be shared
across variables or variable-specific. They may be grid points, quadrature
points, mesh cells, boundary entities, collocation sites, event times, or any
other finite observation object supported by the representation.

The discretized pointwise residual becomes a vector

$$
r_\rho = f(\operatorname{JetBundle}_h(\mathbf{q}, \boldsymbol{\rho}), \theta),
$$

and the discretized integral becomes a reducer over finite observations

$$
J_h(\mathbf{q}) = R_h\left(\boldsymbol{\rho} \mapsto f(\operatorname{JetBundle}_h(\mathbf{q}, \boldsymbol{\rho}), \theta)\right).
$$

## Core Concepts

### `FiniteRepresentation`

Defines how one named continuous variable is represented by finite data.

Required fields:

- `parameter_spec`: PyTree structure and shape/dtype constraints for `q`.
- `variable_name`: stable identifier such as `x`, `u`, or `temperature`.
- `domain`: continuous domain metadata such as an interval or mesh.
- `codomain`: output structure of the variable value.
- `supported_derivative_orders`: derivative orders the adapter can expose.
- `evaluate_jet(params, request, orders) -> JetBatch`.

This is the core abstraction. A basis expansion, grid values, a spline, a
neural network, an ODE-integrated latent state, or a finite-element space can
all implement the same contract.

### `RepresentationBundle`

Groups the finite representations for all variables consumed by one functional.

Required fields:

- `representations`: mapping from variable name to `FiniteRepresentation`.
- `parameter_spec`: mapping from variable name to parameter PyTree spec.
- `request_policy`: whether observation requests are shared, per-variable, or
  derived from a common request.

This bundle is the replacement for a single coefficient vector. It is the
finite-dimensional domain exposed to optimizers and solvers.

### `ObservationRequest`

Defines where and how finite observations are requested.

Required fields:

- `kind`: for example `points`, `cells`, `boundary`, `events`, or
  `custom_adapter_data`.
- `variable_names`: variables this request applies to, or `None` for all
  compatible variables.
- `payload`: JAX arrays or static metadata needed by the representation.
- `measure`: optional weights, quadrature data, or integration metadata.

Point grids are just one request kind. A weak-form finite-element adapter can
use cells and test functions. An event-based adapter can use event times. A
collocation adapter can use collocation sites.

### `JetEvaluator`

Represents derivative access for one representation bundle.

Required fields:

- `representation_bundle`: finite representation adapters for all variables.
- `orders_by_variable`: derivative orders requested for each variable.
- `requests_by_variable`: observation requests for each variable.
- `evaluate(params_by_variable) -> JetBundle`.

The evaluator may use linear derivative matrices, automatic differentiation,
analytic basis derivatives, weak derivatives, reconstruction followed by
finite differences, or an adapter-specific rule. Linearity is not required by
the top-level design.

### `Jet`

The finite data exposed for one variable at one or more observations.

Fields:

- `t`
- `value`
- derivative entries such as `d1`, `d2`, or named aliases like `dt`
- future higher-order entries as needed

### `JetBundle`

The finite data exposed to a user functional for all variables.

Fields:

- `variables`: mapping from variable name to `Jet`.
- optional shared observation metadata such as `t`.
- optional per-variable observation metadata.

The user-facing function should consume a `JetBundle` rather than raw
positional arguments once the first prototype is stable. For example, use
`bundle["x"].value`, `bundle["x"].dt`, and `bundle["u"].value`. This avoids
fragile conventions like `f(x, dx, y, dy, u, ...)` when variables or
derivative orders change.

### `Functional`

The continuous expression to lower.

Initial callable shape:

```python
Callable[[JetBundle, Params], Array]
```

This can be ordinary Python/JAX code, a decorated function, or a constrained
symbolic expression built from proxy variables. The implementation may use
metaprogramming to infer required variables, derivative orders, output shape,
and reduction kind, provided the result is lowered to the explicit internal
spec before numerical evaluation.

### `DiscreteFunctional`

The finite-dimensional result.

Required fields:

- `parameter_spec`
- `evaluate(params_by_variable, functional_params) -> Array`
- `representation_bundle`
- `observation_request`
- `reducer`
- `required_derivative_orders_by_variable`

This object is the boundary consumed by optimizers and solvers.

## Lowering Pipeline

1. Declare a `RepresentationBundle` containing one `FiniteRepresentation` per
   variable.
1. Declare shared or per-variable `ObservationRequest` objects.
1. Declare derivative orders required by the functional for each variable.
1. Build a `JetEvaluator` from the representation, request, and derivative
   orders.
1. Wrap the user callable with a reducer such as pointwise, quadrature, weak
   residual, or custom reduction.
1. Return a `DiscreteFunctional`.

This keeps all discretization choices explicit. The callable only describes
the mathematical expression at a point; the lowering object decides how that
expression is sampled and reduced.

## Metaprogramming Position

Metaprogramming is a valid authoring interface here. The design should support
three levels, all lowering to the same internal `FunctionalSpec`.

Level 1: explicit metadata.

```python
FunctionalSpec(
    required_derivative_orders={"x": (0, 1), "u": (0,)},
    reduction="pointwise",
)
```

Level 2: decorator and signature-driven metadata.

```python
@functional(required_derivative_orders={"x": (0, 1), "u": (0,)}, reduction="quadrature")
def energy(jet, params):
    x = jet["x"]
    u = jet["u"]
    return 0.5 * params.mass * x.dt @ x.dt + params.control_weight * u.value @ u.value
```

Level 3: symbolic proxy or constrained tracing.

```python
x = variable("x")
u = variable("u")
expr = 0.5 * mass * dot(x.dt, x.dt) + control_weight * dot(u.value, u.value)
spec = lower_expression(expr, reduction="quadrature")
```

The implementation may inspect Python signatures and decorator metadata from
the start. AST or bytecode inspection is also allowed if it is treated as an
optional frontend and emits the same explicit `FunctionalSpec`; it must not be
the only representation of the math.

Metaprogramming must preserve these invariants:

- representation and observation request contracts,
- shape rules,
- vectorization behavior,
- JAX transform compatibility,
- error messages for unsupported derivative orders.

## JAX Compatibility Rules

- The final `evaluate` function should be pure and JAX-transformable.
- Static choices such as derivative order, adapter kind, and request kind
  should live in Equinox static fields or plain dataclass metadata outside
  traced arrays.
- Representation parameters, functional parameters, observation coordinates,
  and reducer weights should be JAX arrays when they participate in
  computation.
- Metaprogramming should run before JAX tracing of the final numerical
  `evaluate` function.
- If a frontend inspects Python function bodies, the extracted result should be
  cached as explicit metadata and the runtime evaluator should not depend on
  repeated source inspection.
- Do not mutate representation adapters or evaluators after construction.

## First Implementation Slice

Implement the smallest useful path without making grids or bases the general
contract:

1. `FiniteRepresentation` protocol
   - defines `parameter_spec` and `evaluate_jet`.
1. `RepresentationBundle`
   - supports at least two named variables with separate parameter PyTrees.
1. `PointObservationRequest`
   - one adapter for point observations.
1. `GridValueRepresentation`
   - a reference adapter, not the canonical model.
   - its parameters happen to be grid values.
1. `Jet` and `JetBundle`
   - supports shared `t`, `x.value`, `x.dt`, and another variable such as
     `u.value`.
1. `@functional` decorator
   - records derivative orders and reduction metadata.
   - preserves the original Python callable for numerical evaluation.
1. optional symbolic proxy helpers
   - support `variable("x").dt` as an expression-building frontend.
1. `lower_pointwise(functional, spec, representation_bundle, request)`
   - returns `DiscreteFunctional`.
1. Tests
   - constant trajectory derivative is zero.
   - linear trajectory derivative is constant on interior points.
   - a two-variable expression using `x`, `dx`, and `u` lowers to a vector over
     point observations.

This slice does not need collocation, symbolic differentiation, higher
derivatives, adaptive requests, or integration by parts. It must leave room for
those adapters without changing the public lowering contract.

## Open Design Questions

- What is the minimal `parameter_spec` shape language for arbitrary PyTrees?
- Should variable names be strings, typed keys, or dataclass fields?
- Should shared observation metadata such as `t` live at bundle level, or be
  repeated in each variable jet?
- Should endpoint derivative behavior be owned by `GridValueRepresentation` or
  by `PointObservationRequest`?
- Should quadrature be part of `DiscreteFunctional`, or a separate reducer?
- Should the first public module live under `model/`, or should a new
  `functional/` package own trajectory discretization?
- Should the function spec be a plain dataclass, an algorithm module config, or
  both with conversion helpers?
- How much AST/source inspection is worth supporting after decorator and
  symbolic-proxy frontends exist?

## Recommended Next Step

Create a minimal `functional_discretization.py` module only after this design is
accepted. The first implementation should include the decorator frontend and
the explicit internal spec together, so metaprogramming is tested as an
authoring path while the finite representation remains inspectable.
