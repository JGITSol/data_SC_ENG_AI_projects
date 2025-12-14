"""Force calculation functions"""
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .particle import Particle


# Physical constants
G_EARTH = 9.81  # m/s^2


def gravity_force(particle: 'Particle', g: float = G_EARTH) -> np.ndarray:
    """
    Calculate gravitational force on particle
    
    Args:
        particle: Particle object
        g: Gravitational acceleration (default: Earth's gravity)
        
    Returns:
        Force vector [Fx, Fy]
    """
    return np.array([0.0, -particle.mass * g])


def friction_force(
    particle: 'Particle', 
    coefficient: float = 0.1
) -> np.ndarray:
    """
    Calculate friction force (simplified drag model)
    
    Args:
        particle: Particle object
        coefficient: Friction coefficient
        
    Returns:
        Force vector [Fx, Fy]
    """
    if np.linalg.norm(particle.velocity) < 1e-6:
        return np.array([0.0, 0.0])
    
    # Friction opposes motion
    direction = particle.velocity / np.linalg.norm(particle.velocity)
    magnitude = coefficient * particle.mass * G_EARTH
    return -magnitude * direction


def spring_force(
    particle: 'Particle',
    anchor: np.ndarray,
    k: float = 10.0,
    rest_length: float = 0.0
) -> np.ndarray:
    """
    Calculate spring force (Hooke's law)
    
    Args:
        particle: Particle object
        anchor: Spring anchor point [x, y]
        k: Spring constant
        rest_length: Natural length of spring
        
    Returns:
        Force vector [Fx, Fy]
    """
    displacement = particle.position - anchor
    distance = np.linalg.norm(displacement)
    
    if distance < 1e-6:
        return np.array([0.0, 0.0])
    
    # F = -k * (x - x0)
    extension = distance - rest_length
    direction = displacement / distance
    return -k * extension * direction


def net_force(*forces: np.ndarray) -> np.ndarray:
    """
    Calculate net force from multiple forces
    
    Args:
        *forces: Variable number of force vectors
        
    Returns:
        Net force vector [Fx, Fy]
    """
    return sum(forces)
