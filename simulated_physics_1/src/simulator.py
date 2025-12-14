"""Simulator for pendulum dynamics"""
import numpy as np
from typing import List, Dict, Tuple
from .pendulum import Pendulum


def rk4_step(pendulum: Pendulum, dt: float) -> None:
    """
    Update pendulum state using 4th order Runge-Kutta method
    
    Args:
        pendulum: Pendulum object to update
        dt: Time step in seconds
    """
    # State vector: [theta, omega]
    theta = pendulum.angle
    omega = pendulum.angular_velocity
    
    def derivatives(state: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate [d(theta)/dt, d(omega)/dt]"""
        curr_theta, curr_omega = state
        
        # d(theta)/dt = omega
        d_theta = curr_omega
        
        # d(omega)/dt = -(g/L)sin(theta) - damping*omega
        gravity_term = -(pendulum.g / pendulum.length) * np.sin(curr_theta)
        damping_term = -pendulum.damping * curr_omega
        d_omega = gravity_term + damping_term
        
        return d_theta, d_omega

    # k1
    k1_theta, k1_omega = derivatives((theta, omega))
    
    # k2
    k2_theta, k2_omega = derivatives((
        theta + 0.5 * dt * k1_theta,
        omega + 0.5 * dt * k1_omega
    ))
    
    # k3
    k3_theta, k3_omega = derivatives((
        theta + 0.5 * dt * k2_theta,
        omega + 0.5 * dt * k2_omega
    ))
    
    # k4
    k4_theta, k4_omega = derivatives((
        theta + dt * k3_theta,
        omega + dt * k3_omega
    ))
    
    # Update state
    pendulum.angle += (dt / 6.0) * (k1_theta + 2*k2_theta + 2*k3_theta + k4_theta)
    pendulum.angular_velocity += (dt / 6.0) * (k1_omega + 2*k2_omega + 2*k3_omega + k4_omega)


def run_simulation(
    pendulum: Pendulum,
    duration: float,
    dt: float = 0.01
) -> Dict[str, List[float]]:
    """
    Run full simulation
    
    Args:
        pendulum: Pendulum object
        duration: Total simulation time
        dt: Time step
        
    Returns:
        Dictionary containing time history of state and energy
    """
    steps = int(duration / dt)
    times = np.linspace(0, duration, steps)
    
    results = {
        'time': [],
        'angle': [],
        'angular_velocity': [],
        'kinetic_energy': [],
        'potential_energy': [],
        'total_energy': []
    }
    
    for t in times:
        # Record state
        results['time'].append(t)
        results['angle'].append(pendulum.angle)
        results['angular_velocity'].append(pendulum.angular_velocity)
        results['kinetic_energy'].append(pendulum.kinetic_energy())
        results['potential_energy'].append(pendulum.potential_energy())
        results['total_energy'].append(pendulum.total_energy())
        
        # Update
        rk4_step(pendulum, dt)
        
    return results
