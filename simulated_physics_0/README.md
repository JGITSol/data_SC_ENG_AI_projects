# Simulated Physics 0: Basic Particle Motion

## Overview
A foundational physics simulation project implementing basic Newtonian mechanics for particle motion in 2D space. This project demonstrates fundamental physics concepts including position, velocity, acceleration, and forces.

## Features
- 2D particle motion simulation
- Basic force calculations (gravity, friction)
- Euler integration for position updates
- Visualization of particle trajectories
- Energy conservation validation

## Physics Concepts
- Newtonian mechanics
- Kinematics equations
- Vector operations
- Numerical integration methods

## Project Structure
```
simulated_physics_0/
├── src/
│   ├── __init__.py
│   ├── particle.py          # Particle class with position/velocity
│   ├── forces.py            # Force calculation functions
│   ├── integrator.py        # Numerical integration methods
│   └── visualizer.py        # Plotting and animation
├── tests/
│   ├── test_particle.py
│   ├── test_forces.py
│   └── test_integration.py
├── config/
│   └── simulation_config.yaml
├── data/
│   └── results/
└── notebooks/
    └── demo.ipynb
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.particle import Particle
from src.forces import apply_gravity
from src.integrator import euler_step
from src.visualizer import plot_trajectory

# Create a particle
particle = Particle(mass=1.0, position=[0, 10], velocity=[5, 0])

# Run simulation
trajectory = []
for _ in range(100):
    force = apply_gravity(particle)
    euler_step(particle, force, dt=0.1)
    trajectory.append(particle.position.copy())

# Visualize
plot_trajectory(trajectory)
```

## Testing

```bash
pytest tests/
```

## Learning Objectives
- Understand basic Newtonian mechanics
- Implement numerical integration
- Validate physics simulations
- Visualize physical systems

## License
MIT License
