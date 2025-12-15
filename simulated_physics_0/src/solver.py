"""
Solver adapter for compatibility with Streamlit app.
Wraps the functional integrators in a class-based interface.
"""
import numpy as np
from typing import TYPE_CHECKING
from .integrator import verlet_step, euler_step

if TYPE_CHECKING:
    from .particle import Particle

class VerletSolver:
    """
    Verlet integration solver.
    Maintains state required for Verlet integration (previous position).
    """
    def __init__(self, dt: float):
        self.dt = dt
        self.previous_positions = {}  # Map particle ID to previous position

    def step(self, particle: 'Particle', force: np.ndarray) -> None:
        """
        Advance the particle by one time step.
        """
        # Use object id as key for simple state tracking
        pid = id(particle)
        prev_pos = self.previous_positions.get(pid)
        
        # Store current position before update to become next previous
        current_pos = particle.position.copy()
        
        verlet_step(particle, force, self.dt, prev_pos)
        
        # Update previous position for next step
        self.previous_positions[pid] = current_pos

class EulerSolver:
    """
    Euler integration solver.
    """
    def __init__(self, dt: float):
        self.dt = dt

    def step(self, particle: 'Particle', force: np.ndarray) -> None:
        euler_step(particle, force, self.dt)
