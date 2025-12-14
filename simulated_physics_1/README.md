# Simulated Physics 1: Pendulum Motion

## Overview
Simulation of simple and compound pendulum systems demonstrating periodic motion, energy transfer, and small-angle approximations.

## Features
- Simple pendulum simulation
- Large-angle vs small-angle comparisons
- Energy oscillation between kinetic and potential
- Phase space diagrams
- Period calculations and validation

## Physics Concepts
- Angular motion
- Harmonic oscillators
- Conservation of energy
- Small-angle approximation
- Restoring forces

## Key Equations
- `θ'' + (g/L)sin(θ) = 0` (nonlinear pendulum)
- `T = 2π√(L/g)` (small-angle period)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from src.pendulum import Pendulum
from src.simulator import run_simulation

pendulum = Pendulum(length=1.0, mass=1.0, angle=0.3, angular_velocity=0)
results = run_simulation(pendulum, duration=10.0, dt=0.01)
```

## License
MIT License
