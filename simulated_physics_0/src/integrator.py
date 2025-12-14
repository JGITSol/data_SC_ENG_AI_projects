"""Numerical integration methods for physics simulation"""
import numpy as np
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .particle import Particle


def euler_step(
    particle: 'Particle',
    force: np.ndarray,
    dt: float
) -> None:
    """
    Update particle state using Euler integration
    
    Args:
        particle: Particle to update
        force: Net force acting on particle
        dt: Time step
    """
    # Update acceleration from force
    particle.apply_force(force)
    
    # Update velocity: v(t+dt) = v(t) + a*dt
    particle.velocity += particle.acceleration * dt
    
    # Update position: x(t+dt) = x(t) + v*dt
    particle.position += particle.velocity * dt


def verlet_step(
    particle: 'Particle',
    force: np.ndarray,
    dt: float,
    previous_position: np.ndarray = None
) -> None:
    """
    Update particle state using Verlet integration (more accurate for oscillations)
    
    Args:
        particle: Particle to update
        force: Net force acting on particle
        dt: Time step
        previous_position: Position at previous time step
    """
    particle.apply_force(force)
    
    if previous_position is None:
        # First step: fall back to Euler
        euler_step(particle, force, dt)
    else:
        # Verlet: x(t+dt) = 2*x(t) - x(t-dt) + a*dt^2
        new_position = (2 * particle.position - 
                       previous_position + 
                       particle.acceleration * dt**2)
        
        # Update velocity from position change
        particle.velocity = (new_position - particle.position) / dt
        particle.position = new_position


def rk4_step(
    particle: 'Particle',
    force_func: Callable,
    dt: float
) -> None:
    """
    Update particle state using 4th order Runge-Kutta integration
    
    Args:
        particle: Particle to update
        force_func: Function that takes particle and returns force
        dt: Time step
    """
    # Store original state
    pos0 = particle.position.copy()
    vel0 = particle.velocity.copy()
    
    # k1
    f1 = force_func(particle)
    a1 = f1 / particle.mass
    v1 = vel0
    
    # k2
    particle.position = pos0 + 0.5 * v1 * dt
    particle.velocity = vel0 + 0.5 * a1 * dt
    f2 = force_func(particle)
    a2 = f2 / particle.mass
    v2 = vel0 + 0.5 * a1 * dt
    
    # k3
    particle.position = pos0 + 0.5 * v2 * dt
    particle.velocity = vel0 + 0.5 * a2 * dt
    f3 = force_func(particle)
    a3 = f3 / particle.mass
    v3 = vel0 + 0.5 * a2 * dt
    
    # k4
    particle.position = pos0 + v3 * dt
    particle.velocity = vel0 + a3 * dt
    f4 = force_func(particle)
    a4 = f4 / particle.mass
    v4 = vel0 + a3 * dt
    
    # Combine
    particle.position = pos0 + (dt / 6) * (v1 + 2*v2 + 2*v3 + v4)
    particle.velocity = vel0 + (dt / 6) * (a1 + 2*a2 + 2*a3 + a4)
