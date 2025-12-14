"""Particle class for physics simulation"""
import numpy as np
from typing import List, Tuple


class Particle:
    """Represents a particle with mass, position, and velocity"""
    
    def __init__(
        self, 
        mass: float = 1.0,
        position: List[float] = None,
        velocity: List[float] = None
    ):
        """
        Initialize a particle
        
        Args:
            mass: Particle mass in kg
            position: Initial position [x, y] in meters
            velocity: Initial velocity [vx, vy] in m/s
        """
        self.mass = mass
        self.position = np.array(position if position else [0.0, 0.0], dtype=float)
        self.velocity = np.array(velocity if velocity else [0.0, 0.0], dtype=float)
        self.acceleration = np.array([0.0, 0.0], dtype=float)
        
    def apply_force(self, force: np.ndarray) -> None:
        """Apply force to particle using F = ma"""
        self.acceleration = force / self.mass
        
    def kinetic_energy(self) -> float:
        """Calculate kinetic energy: KE = 0.5 * m * v^2"""
        speed_squared = np.dot(self.velocity, self.velocity)
        return 0.5 * self.mass * speed_squared
        
    def momentum(self) -> np.ndarray:
        """Calculate momentum: p = m * v"""
        return self.mass * self.velocity
        
    def __repr__(self) -> str:
        return (f"Particle(mass={self.mass}, "
                f"pos={self.position}, "
                f"vel={self.velocity})")
