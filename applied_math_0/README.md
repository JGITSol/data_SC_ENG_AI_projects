# Applied Mathematics 0: Numerical Methods

## Overview
Implementation of fundamental numerical methods for solving equations, interpolation, differentiation, and integration.

## Features
- Root finding (bisection, Newton-Raphson, secant method)
- Numerical differentiation (forward, backward, central difference)
- Numerical integration (trapezoidal, Simpson's rule, Gaussian quadrature)
- Linear interpolation and spline interpolation
- Error analysis and convergence rates

## Mathematical Topics
- Root finding algorithms
- Finite difference methods
- Numerical quadrature
- Interpolation theory
- Truncation and round-off errors

## Key Methods
- **Bisection**: Guaranteed convergence, slow
- **Newton-Raphson**: Fast convergence (quadratic), requires derivative
- **Trapezoidal Rule**: O(h²) accuracy
- **Simpson's Rule**: O(h⁴) accuracy

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from src.root_finding import newton_raphson
from src.integration import simpsons_rule

# Find root of f(x) = x^2 - 2
root = newton_raphson(lambda x: x**2 - 2, x0=1.0)

# Integrate function
result = simpsons_rule(lambda x: x**2, a=0, b=1, n=100)
```

## License
MIT License
